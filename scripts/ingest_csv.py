#!/usr/bin/env python3
"""Ingest CSV assessor exports into Postgres raw tables."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv", type=Path, help="Input CSV file (assessor export)")
    parser.add_argument("locality", help="Locality slug (e.g., exeter-nh)")
    parser.add_argument(
        "--source-name",
        default="assessor_export",
        help="Logical source label saved to ingest.raw_files",
    )
    parser.add_argument(
        "--db-url",
        default=os.environ.get("HOUSING_DB_URL", "postgresql+psycopg://dkovar@localhost/housing"),
        help="SQLAlchemy database URL",
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=500,
        help="Upsert chunk size so we do not overwhelm the database",
    )
    return parser.parse_args()


def compute_file_hash(path: Path) -> str:
    sha = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            sha.update(chunk)
    return sha.hexdigest()


def upsert_raw_properties(engine, locality: str, file_id: int, df: pd.DataFrame, chunk_size: int) -> None:
    df = df.astype(object).where(pd.notna(df), None)
    records = df.to_dict(orient="records")
    stmt = text(
        """
        INSERT INTO ingest.raw_properties (locality, property_id, payload, source_file_id)
        VALUES (:locality, :property_id, CAST(:payload AS jsonb), :source_file_id)
        ON CONFLICT (locality, property_id)
        DO UPDATE
            SET payload = EXCLUDED.payload,
                source_file_id = EXCLUDED.source_file_id,
                ingested_at = now();
        """
    )

    with engine.begin() as conn:
        for i in range(0, len(records), chunk_size):
            chunk = records[i : i + chunk_size]
            payloads = [
                {
                    "locality": locality,
                    "property_id": row.get("id") or row.get("property_id") or f"row-{i+j}",
                    "payload": json.dumps(row, default=str),
                    "source_file_id": file_id,
                }
                for j, row in enumerate(chunk)
            ]
            conn.execute(stmt, payloads)


def main() -> None:
    args = parse_args()
    if not args.csv.exists():
        raise SystemExit(f"CSV not found: {args.csv}")

    df = pd.read_csv(args.csv)
    file_hash = compute_file_hash(args.csv)

    engine = create_engine(args.db_url)
    with engine.begin() as conn:
        result = conn.execute(
            text(
                """
                INSERT INTO ingest.raw_files (locality, source_name, source_path, file_hash, row_count)
                VALUES (:locality, :source_name, :source_path, :file_hash, :row_count)
                RETURNING id
                """
            ),
            {
                "locality": args.locality,
                "source_name": args.source_name,
                "source_path": str(args.csv),
                "file_hash": file_hash,
                "row_count": len(df),
            },
        )
        file_id = result.scalar_one()

    upsert_raw_properties(engine, args.locality, file_id, df, args.chunk_size)
    print(f"✔ Loaded {len(df):,} rows from {args.csv} into ingest.raw_properties (file_id={file_id})")


if __name__ == "__main__":
    main()
