# Locality Configuration Format

Config files live under `localities/<slug>.yml` and capture any assumptions that should **not** live in Python code. The loader (to be implemented) should validate these files before applying overrides.

## File Skeleton
```yaml
slug: exeter-nh            # machine slug used in URLs + DB keys
name: Exeter, New Hampshire # human-facing label
description: >
  Baseline overrides derived from the 2024 assessor export.
cleaning:
  drop_if_address_line2_prefix: ["ste"]
  drop_if_address_line1_regex:
    - pattern: "(?i)^P\\.?\\s*O\\.?\\s*Box"
      reason: "PO boxes are mailing addresses, not physical housing units"
  property_type_overrides:
    - match: "11 Boulder Brook Dr"
      type: literal        # literal | regex
      new_value: "Townhouse"
  drop_records:
    - match: "1 Hampton Rd"
      type: literal
schema:
  inferred_default_year_built: 1600
  auto_apartment_from_address2_prefix:
    prefix: "apt"
    new_value: "Apartment"
  solo_condo_behaviour: townhouse   # townhouse | leave | drop
refresh:
  assessor_export:
    url: s3://…
    cadence: quarterly
  rentcast:
    radius_miles: 10
    schedule: weekly
```

## Field Reference

### Top-level identity
| Field | Required | Notes |
|-------|----------|-------|
| `slug` | ✅ | Used in DB keys and API routing. Lowercase + hyphen recommended. |
| `name` | ✅ | Display name. |
| `description` | ➖ | Markdown-friendly short blurb. |

### `cleaning` section
| Key | Type | Purpose |
|-----|------|---------|
| `drop_if_address_line2_prefix` | list[str] | Case-insensitive prefixes (e.g., `ste`) to drop. |
| `drop_if_address_line1_regex` | list[{pattern, reason?}] | Regex-based drop filters for address line 1. |
| `property_type_overrides` | list[{match, type, new_value, reason?}] | Reassign property types for literal or regex matches. |
| `drop_records` | list[{match, type, reason?}] | Hard drops for known non-residential entries. |
| `promote_apartments` | bool or object | Controls `promote_apartment_buildings` helper + overrides (thresholds, regex). |
| `unknown_property_type_fallback` | string | e.g., `Unknown`, `Needs review`. |

### `schema` section
| Field | Description |
|-------|-------------|
| `inferred_default_year_built` | Integer fallback when data is missing/invalid. |
| `auto_apartment_from_address2_prefix` | Object with `prefix` + `new_value` toggling the apartment inference rule. |
| `solo_condo_behaviour` | Enum controlling what to do with single-record condos (`townhouse`, `leave`, `drop`). |
| `coerce_numeric` | List of column names to `pd.to_numeric` (default: bedrooms, bathrooms, yearBuilt). |

### `refresh` section (future use)
Defines how to pull raw data per locality (assessor exports, RentCast, zoning layers). Include URLs, access instructions, and cadence (e.g., `monthly`, `quarterly`).

## Validation Rules
- Require `slug` uniqueness and forbid spaces.
- Enforce `type` to be either `literal` or `regex` in override/drop lists.
- Fail fast if regex patterns do not compile.
- Provide sensible defaults when optional blocks are omitted (e.g., keep global PO Box drop if `drop_if_address_line1_regex` missing).

## Next Steps
1. Build a loader that reads `<locality>.yml`, validates against a Pydantic (or similar) schema, and applies overrides inside `clean_housing_data`.
2. Update tests/notebooks to ensure every Exeter-specific rule in Python has a config counterpart.
3. Add documentation for new localities so others can copy/paste from this spec.
