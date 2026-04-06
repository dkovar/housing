# Repo Audit — 2026-04-06

A quick inventory of the `housing` Streamlit application so we know what already exists before planning new work.

## Purpose & Entry Points
- `app.py` is the Streamlit entrypoint. It loads `table.csv`, runs `clean.clean_housing_data`, and exposes navigation for landing, data tables, charts, and supporting copy.
- Pages are implemented under `views/` as paired `.py` + `.md` modules (e.g., `landing`, `background`, `todo`). Navigation state is tracked via `st.session_state.page`.

## Dependencies & Runtime
- Python 3.11 conda env named `housing` (per README).
- Requirements (see `requirements.txt`): Streamlit 1.33+, pandas 2.x, numpy 1.24+, matplotlib, folium + streamlit-folium for mapping, chardet, asttokens, optional GeoPandas/Shapely, SQLAlchemy 2.x + psycopg 3.2, BeautifulSoup4.
- Assumes a local Postgres database `housing` reachable via `HOUSING_DB_URL`.

## Data Assets
- `table.csv`, `values.csv`: current CSV snapshots backing the Streamlit demo.
- `data_sources/planning_board_minutes.json`: scraped Planning Board agenda/minute metadata (see `scripts/fetch_minutes_index.py`).
- `localities/exeter.yml`: first cut at a locality-specific cleaning/config file.
- `db/schema.sql`: logical schema splitting `ingest` (raw files/properties) and `curated` (clean properties) schemas.

## Cleaning & Transformation
- `clean.py` handles dict parsing, architecture extraction, a long list of Exeter-specific overrides/drops, PO Box filtering, apartment/condo heuristics, normalization, numeric coercion, and helper routines (`promote_apartment_buildings`, `find_missing_unit_with_matching_record`).
- `docs/cleaning_rules.md` catalogs each cleaning rule, flags whether it is generic or Exeter-specific, and sketches the desired config fields.
- `filters.py` exposes sidebar filters for property type, bedroom/bath ranges, and year built.

## Views / UI
- `views/raw_data.py` compares before/after/filter summaries and highlights "Unknown" clusters.
- `views/pie_chart.py`, `views/bar_by_year.py`, `views/other_charts.py`, `views/map_view.py` supply basic visualizations.
- `views/background.md`, `views/landing.md`, and `views/todo.md` hold narrative copy.

## Supporting Scripts
- `scripts/fetch_minutes_index.py`: resilient scraper for exeternh.gov meeting listings with retries/user-agent rotation.
- `scripts/ingest_csv.py`: CSV → Postgres ingestion. Registers a raw file, computes SHA-256, upserts rows into `ingest.raw_properties` in chunks.

## Observations & Gaps
- App currently loads CSVs directly; Streamlit is not yet hitting Postgres or any API endpoints.
- Cleaning rules are hard-coded in Python even though `localities/exeter.yml` exists. Need a loader + validation layer.
- No caching around `load_data`/`clean_housing_data`; repeated reruns re-read CSV.
- There is no orchestration for scheduled scraping, CSV ingestion, or RentCast enrichment yet.
- Tests are absent; there is also no lint/format tooling configured.

Use this as the baseline for deciding what to refactor versus what to build next.
