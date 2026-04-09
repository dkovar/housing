# Cleaning Rules Inventory

This document breaks down the current `clean_housing_data` pipeline into reusable stages.
For each stage we flag whether it is **generic** (should apply to any locality) or **Exeter-local** (needs to move into a locality config file).

| Order | Rule | Type | Notes |
|-------|------|------|-------|
| 1 | Parse dict-like columns (`features`, `taxAssessments`, `propertyTaxes`, `owner`) into Python dicts via `safe_parse_to_dict`. | Generic | Should stay in core pipeline. |
| 2 | Derive `architectureType` from `features` dict. | Generic | Could move to a derived-features module later. |
| 3 | Drop rows where `addressLine2` starts with `Ste` (assume commercial/office). | Exeter-local | Should become a locality config rule (`drop_if_address_line2_prefix`). |
| 4 | Apply hard-coded overrides/drops for specific `addressLine1` patterns (e.g., `11 Boulder Brook Dr → Townhouse`, `1 Hampton Rd → DROP`). | Exeter-local | Needs YAML-driven mapping with support for literal and regex matches. |
| 5 | Drop any row whose `addressLine1` matches `PO Box`. | Generic | Keep as global rule. |
| 6 | If `addressLine2` starts with `Apt` and `propertyType` is missing → set to `Apartment`. | Generic | Reasonable default but should be toggleable. |
| 7 | Single-row Condos become `Townhouse`. | Exeter-local | This assumption was based on local data quirks. Should be configurable or replaced with heuristics keyed by zoning. |
| 8 | Normalize `propertyType` strings: strip, fill empty with `Unknown`. | Generic | Core hygiene. |
| 9 | Coerce `bedrooms`, `bathrooms`, `yearBuilt` to numeric (fill empties). | Generic | Keep. |
| 10 | Apartment promotion helpers (`promote_apartment_buildings`, `find_missing_unit_with_matching_record`). | Generic-ish | Logic is general but thresholds/regexes should be parameterized. |

## Proposed Config Fields

A future `localities/<slug>/cleaning.yml` could include:

```yaml
name: exeter-nh
ste_drop_prefixes:
  - "ste"
address_overrides:
  - match: "11 Boulder Brook Dr"
    type: literal
    action: set_property_type
    value: "Townhouse"
  - match: "1 Hampton Rd"
    type: literal
    action: drop
  - match: "^.*Stonewall Way"
    type: regex
    action: set_property_type
    value: "Townhouse"
po_box_drop: true
apt_infer_property_type: "Apartment"
solo_condo_behavior: "townhouse"  # or null to disable
promote_apartments: true
```

Next step: lift the hard-coded `updates` list + STE drop rule into a config loader so other towns can provide their own instructions without touching Python code.
