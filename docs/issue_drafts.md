# Issue Drafts (pending GitHub auth)

1. **Implement locality-config-driven cleaning**
   - *Summary*: Load `localities/<slug>.yml`, validate with Pydantic, and apply overrides inside `clean_housing_data` (drop rules, property type overrides, condo/apartment heuristics).
   - *Details*: Include unit tests covering literal + regex matches, and add a CLI switch or Streamlit sidebar to change locality. Document the format in `docs/locality_config.md`.

2. **Back Streamlit with Postgres / API**
   - *Summary*: Replace `table.csv` with live queries against `curated.properties` (or a small FastAPI proxy) so the UI reflects fresh data.
   - *Details*: Add connection config via env vars, implement caching, and ensure download/export buttons work against the live source.

3. **Automate ingestion + enrichment jobs**
   - *Summary*: Script/schedule assessor CSV ingestion, RentCast enrichment, and planning-board scraping with logging + status indicators.
   - *Details*: Start with a Makefile or Taskfile, then follow up with GitHub Actions or cron once we have infrastructure. Surface latest-run timestamps in the UI.
