# Exeter MVP User Stories (2026-04-06)

## Residents curious about housing mix
1. **Browse property types at a glance**
   - *Story*: As a resident, I want to see how many Single Family vs. Condo vs. Apartment units exist so I can understand Exeter's current mix.
   - *Acceptance*: Landing page shows a pie/bar chart sourced from cleaned data with totals and explanatory copy; filters update the visuals immediately.

2. **Search for my street/building**
   - *Story*: As a resident, I want to look up my street to confirm how a property is classified.
   - *Acceptance*: Raw Data view provides search/filter controls (address substring, property type) and displays both raw + cleaned classifications.

## Planning Board & Town Staff
3. **Identify data-quality gaps**
   - *Story*: As a planner, I need to quickly see which records are `Unknown` or missing bedrooms/bathrooms so I can prioritize cleanup.
   - *Acceptance*: Summary table flags unknown clusters (top 5 addresses) plus counts of records missing key fields, exportable as CSV.

4. **Track changes over time**
   - *Story*: As staff, I want to compare year-built cohorts to understand how much housing stock is pre-/post-2000.
   - *Acceptance*: Property Type by Year chart shows stacked bars with hover details; filters persist when switching pages.

## Advocates / Task Force Members
5. **Surface large multifamily buildings**
   - *Story*: As a housing advocate, I want to identify apartment buildings (vs. individual units) to discuss large-site opportunities.
   - *Acceptance*: Map/table highlight promoted apartment-building records with counts of associated units and rents (once enrichment lands).

6. **Download cleaned dataset**
   - *Story*: As a volunteer analyst, I want to export the cleaned, filtered dataset to run my own analysis.
   - *Acceptance*: Provide a "Download filtered CSV" button that respects the current filter set and includes metadata (timestamp, filters applied).

## Stretch (post-MVP)
- Enriched rent/value trends (RentCast or MLS overlays).
- Compare Exeter against peer towns once locality configs exist.
- Embed planning board meeting feed (from `data_sources/planning_board_minutes.json`).
