#!/usr/bin/env python3
"""Fetch Planning Board meeting metadata from exeternh.gov."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
import sys
import time

import requests
from bs4 import BeautifulSoup
from dateutil.relativedelta import relativedelta
from requests.adapters import HTTPAdapter, Retry

BASE_URL = "https://www.exeternh.gov/meetings"
PLANNING_DEPT_ID = "421"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--start-date",
        default=(datetime.now(timezone.utc) - relativedelta(years=5)).date().isoformat(),
        help="ISO date (YYYY-MM-DD) to stop at (older entries are ignored)",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=200,
        help="Safety cap on paginated result pages to fetch",
    )
    parser.add_argument(
        "--output",
        default="data_sources/planning_board_minutes.json",
        help="Path to write JSON array of meeting metadata",
    )
    return parser.parse_args()


session = requests.Session()
retry = Retry(
    total=5,
    backoff_factor=1.0,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET"],
)
adapter = HTTPAdapter(max_retries=retry)
session.mount("https://", adapter)
session.mount("http://", adapter)


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


def fetch_page(page: int) -> BeautifulSoup:
    params = {
        "field_department_target_id": PLANNING_DEPT_ID,
        "page": page,
    }
    for attempt in range(5):
        try:
            resp = session.get(BASE_URL, params=params, headers=HEADERS, timeout=30)
            resp.raise_for_status()
            return BeautifulSoup(resp.text, "html.parser")
        except requests.exceptions.RequestException:
            if attempt == 4:
                raise
            time.sleep(2 ** attempt)
    raise RuntimeError("unreachable")


def extract_rows(soup: BeautifulSoup):
    table = soup.find("table", class_="views-table")
    if not table:
        return []
    return table.find("tbody").find_all("tr")


def parse_row(row, cutoff: datetime):
    date_cell = row.find("td", class_="views-field-field-calendar-date")
    if not date_cell:
        return None
    span = date_cell.find("span", class_="date-display-single")
    if not span:
        return None
    iso = span.get("content")
    if not iso:
        return None
    run_dt = datetime.fromisoformat(iso)
    if run_dt < cutoff:
        return "older"

    meeting_name = row.find("td", class_="views-field-title")
    if not meeting_name:
        return None
    title = meeting_name.get_text(strip=True)
    if "Planning Board" not in title:
        return None

    def _links(td_class: str):
        td = row.find("td", class_=td_class)
        if not td:
            return []
        return [a.get("href") for a in td.find_all("a") if a.get("href")]

    view_td = row.find("td", class_="views-field-view-node")
    detail_path = None
    if view_td and (link := view_td.find("a")):
        detail_path = link.get("href")

    return {
        "meeting_date": run_dt.isoformat(),
        "title": title,
        "detail_url": f"https://www.exeternh.gov{detail_path}" if detail_path else None,
        "agendas": _links("views-field-field-agendas"),
        "minutes": _links("views-field-field-minutes"),
        "packets": _links("views-field-field-packets"),
        "video": _links("views-field-field-video-link"),
    }


def main() -> None:
    args = parse_args()
    cutoff = datetime.fromisoformat(args.start_date).replace(tzinfo=timezone.utc)
    data = []
    stop = False

    for page in range(args.max_pages):
        print(f"Fetching meeting page {page}…", file=sys.stderr)
        soup = fetch_page(page)
        rows = extract_rows(soup)
        if not rows:
            break
        for row in rows:
            parsed = parse_row(row, cutoff)
            if parsed == "older":
                stop = True
                break
            if parsed:
                data.append(parsed)
        if stop:
            break

    output_path = args.output
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"Saved {len(data)} planning board meetings to {path}")


if __name__ == "__main__":
    main()
