# Housing Data Explorer

Public-facing Streamlit app plus ingestion/cleaning tooling for Exeter, NH housing data (with an eye toward generalizing to other municipalities).

## Local setup

1. **Python environment**
   - Install Miniforge (already at `~/miniforge3`).
   - Create/activate the project env: `conda activate housing` (Python 3.11).
   - Install deps: `pip install -r requirements.txt` (SQLAlchemy + psycopg included).
2. **Postgres**
   - Local cluster with `psql` on PATH.
   - Database: `housing` (created locally).
   - Connection env vars (example):
     ```bash
     export HOUSING_DB_URL="postgresql+psycopg://dkovar@localhost/housing"
     ```
3. **Streamlit app**
   ```bash
   conda activate housing
   streamlit run app.py
   ```

## Repo layout

```
app.py                  # Streamlit entry point
clean.py                # Cleaning + normalization helpers
data_loader.py         # CSV loader + validation
filters.py              # Sidebar filters
views/                  # Page renderers + markdown copy
docs/cleaning_rules.md  # Breakdown of cleaning logic
localities/             # Town-specific overrides (starting with Exeter)
```

## Roadmap snapshot

- [x] Conda env (`housing`) + requirements updated to include SQLAlchemy + psycopg.
- [x] Local Postgres database created (`housing`).
- [ ] Lift hard-coded cleaning rules into config (`localities/*.yml`).
- [ ] Build ingestion script to load assessor CSV into Postgres tables.
- [ ] Add RentCast-based enrichment (weekly, 10-mile radius, Exeter) once API key provided.
- [ ] Generalize UI to select locality + dataset.

See `projects/housing/README.md` in the workspace root for broader project context.
