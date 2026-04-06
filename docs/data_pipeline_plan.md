# Data Pipeline Plan (2026-04-06)

## Goals
1. Keep raw assessor exports intact for auditability.
2. Normalize/clean data into a `curated` schema the app can query.
3. Enrich with external signals (RentCast, zoning, meeting notes) on a predictable cadence.
4. Automate refresh and surface status/alerts.

## Sources
| Source | Format | Access | Cadence | Notes |
|--------|--------|--------|---------|-------|
| Town assessor export | CSV (~10–15 MB) | Manual pull today; aim for S3 or emailed link | Quarterly | Columns align with current `table.csv`. Need data dictionary. |
| Planning Board meetings | HTML pages | `scripts/fetch_minutes_index.py` | Weekly | Already writing to `data_sources/planning_board_minutes.json`. |
| RentCast API | REST | Requires API key | Weekly | Pull median rent, comps within 10-mile radius. |
| Zoning / parcels | Shapefile/GeoJSON | Town GIS or NH GRANIT | Annual | Needed for map overlays + ADU reasoning. |

## Target Schemas (per `db/schema.sql`)
- `ingest.raw_files`: log of every file ingested (locality, hash, row count).
- `ingest.raw_properties`: JSON payload per property keyed by `(locality, property_id)`.
- `curated.properties`: flattened + cleaned dataset used by Streamlit.

## Pipeline Stages
1. **Acquisition**
   - Store raw files under `data/raw/<locality>/<yyyymmdd>/...`.
   - Record metadata via `ingest.raw_files` (already supported by `scripts/ingest_csv.py`).
2. **Landing in Postgres**
   - Use `scripts/ingest_csv.py` (chunked upserts) for assessor exports.
   - Build equivalent loaders for future sources (e.g., RentCast snapshot table, meeting index table).
3. **Cleaning & Normalization**
   - Implement locality config loader (see `docs/locality_config.md`).
   - Run `clean_housing_data` against the raw payload (pandas or SQL-based) and write results to `curated.properties` along with derived metadata (unknown flags, building/unit relationships).
4. **Enrichment**
   - RentCast: store results plus retrieval timestamp, link to `property_id` via lat/long or address.
   - GIS overlays: attach zoning district, lot size, overlay flags to `derived` JSON.
   - Meeting metadata: maintain separate table for planning board items, keyed by meeting date, to embed in the UI.
5. **Serving Layer**
   - Expose a lightweight API (FastAPI or Supabase) or let Streamlit query Postgres directly via SQLAlchemy with caching.
   - Add health/status ping to confirm latest refresh time per locality.

## Automation Roadmap
- **Phase 1 (manual)**: Run ingestion + cleaning notebooks locally; export `table.csv` for Streamlit.
- **Phase 2 (semi-automated)**: Shell script/Makefile orchestrates `fetch_minutes_index`, `ingest_csv`, `clean -> curated export`.
- **Phase 3 (scheduled)**: GitHub Actions or Airflow runs nightly/weekly jobs, pushes sanitized CSV/Parquet to object storage.

## Open Questions
- Where will long-term storage live? (S3 bucket vs. local NAS.)
- What authentication will the Streamlit app need to reach Postgres if deployed publicly?
- Do we need row-level change tracking (e.g., `effective_date`) to analyze deltas over time?

Use this plan to create tickets/automation tasks as we wire up the full pipeline.
