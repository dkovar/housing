# clean.py
import pandas as pd
import ast
import numpy as np
import re

DICT_COLUMNS = ["features", "taxAssessments", "propertyTaxes", "owner"]

def safe_parse(value):
    try:
        if pd.notna(value) and isinstance(value, str) and value.strip().startswith("{"):
            return ast.literal_eval(value)
    except Exception:
        pass
    return {}
    
def safe_parse_to_dict(x):
    if pd.isna(x):
        return {}
    if isinstance(x, dict):
        return x
    if isinstance(x, str):
        s = x.strip()
        if s.startswith("{") and s.endswith("}"):
            # try JSON first
            try:
                return json.loads(s)
            except json.JSONDecodeError:
                # fallback for single-quoted / python-literal dicts
                try:
                    return ast.literal_eval(s)
                except Exception:
                    return {}
    return {}


def clean_housing_data(df: pd.DataFrame) -> pd.DataFrame:
    # Work on our own copy
    df = df.copy()

    # 1) Parse dict-like columns into dicts
    for col in DICT_COLUMNS:
        if col in df.columns:
            df.loc[:, col] = df[col].apply(safe_parse_to_dict)

    # Extract the architectureType from features and make it its own column
    df["architectureType"] = df["features"].apply(
        lambda d: d.get("architectureType") if isinstance(d, dict) else None
    )
    
    # 2) Drop rows where addressLine2 starts with "Ste" (offices)
    if "addressLine2" in df.columns:
        ste_mask = df["addressLine2"].astype(str).str.strip().str.lower().str.startswith("ste", na=False)
        df = df.loc[~ste_mask].copy()

    # 3) Known manual fixes (drops + type updates)
    updates = [
        ("11 Boulder Brook Dr", "Townhouse"),
        ("1 Hampton Rd", "DROP"),
        ("117 Water St", "DROP"),
        ("6 White Oak Dr", "Assisted Living"),
        ("7 Riverwoods Dr", "Assisted Living"),
        ("17 Hampton Rd", "Assisted Living"),
        ("40 Hampton Rd", "Manufactured"),
        ("11 Court St", "DROP"),
        ("16 Kingston Rd", "DROP"),
        ("8 Continental Dr", "DROP"),
        ("27 Front St", "DROP"),
        # Wildcard examples:
        (r".?. Deep Mdws", "Manufactured"),
        (r"Exeter River Lndg", "Manufactured"),
        (r"^.*Stonewall Way", "Townhouse"),
        (r"\d Timber Ln", "Assisted Living"),
        (r"Stonearch At Hidden Mdw?", "Single Family (Planning)")
    ]
    
    if "addressLine1" in df.columns:
        for pattern, new_type in updates:
            # Build mask for this pattern (regex match, case-insensitive)
            mask = df["addressLine1"].astype(str).str.contains(pattern, case=False, na=False, regex=True)
    
            if new_type == "DROP":
                df = df.loc[~mask].copy()
            else:
                df.loc[mask, "propertyType"] = new_type
            
    # 4) Drop all PO Box records (by addressLine1)
    df = df[~df["addressLine1"].str.contains(r"(?i)^P\.?\s*O\.?\s*Box", na=False)]

    # 5) If address is an apartment and propertyType is missing → set to "Apartment"
    if "addressLine2" in df.columns and "propertyType" in df.columns:
        apt_mask = df["propertyType"].isna() & df["addressLine2"].astype(str).str.strip().str.lower().str.startswith("apt", na=False)
        df.loc[apt_mask, "propertyType"] = "Apartment"

    # 6) Single-record condos → Townhouse
    if "addressLine1" in df.columns and "propertyType" in df.columns:
        group_counts = df.groupby("addressLine1", dropna=False)["addressLine1"].transform("count")
        one_row_condo = (group_counts == 1) & (df["propertyType"].astype(str).str.lower() == "condo")
        df.loc[one_row_condo, "propertyType"] = "Townhouse"

    # 7) Normalize propertyType
    if "propertyType" not in df.columns:
        df["propertyType"] = "Unknown"
    else:
        df.loc[:, "propertyType"] = (
            df["propertyType"]
            .astype(object)
            .apply(lambda x: x.strip() if isinstance(x, str) else x)
            .fillna("")
            .replace("", "Unknown")
        )

    # 8) Numeric fields
    if "bedrooms" in df.columns:
        df.loc[:, "bedrooms"] = pd.to_numeric(df["bedrooms"], errors="coerce").fillna(0).astype(int)
    if "bathrooms" in df.columns:
        df.loc[:, "bathrooms"] = pd.to_numeric(df["bathrooms"], errors="coerce").fillna(0)
    if "yearBuilt" in df.columns:
        df.loc[:, "yearBuilt"] = pd.to_numeric(df["yearBuilt"], errors="coerce").fillna(1600).astype(int)

    return df
    
def promote_apartment_buildings(df: pd.DataFrame) -> pd.DataFrame:
    """
    For each addressLine1 group where:
      - at least one addressLine2 starts with 'Apt' (case-insensitive), and
      - NO null addressLine2 exists in that group,

    create a new 'Apartment building' record (duplicating the first row but nulling
    addressLine2/bedrooms/bathrooms/squareFootage), set all existing rows in the
    group to 'Apartment unit', and set the building row's id to the original id
    with the addressLine2 segment removed (no synthetic suffix).
    """
    df = df.copy()

    if "propertyType" not in df.columns:
        df["propertyType"] = "Unknown"

    groups = df.groupby("addressLine1", dropna=False)

    starts_with_apt = groups["addressLine2"].transform(
        lambda s: s.dropna().astype(str).str.strip().str.lower().str.startswith("apt").any()
    )
    no_null_addr2 = groups["addressLine2"].transform(lambda s: s.isna().sum() == 0)

    eligible = starts_with_apt & no_null_addr2
    eligible_keys = df.loc[eligible, "addressLine1"].dropna().unique()

    def _normalize_addr2_for_id(addr2: str) -> str:
        # "Apt 11" -> "Apt-11" to match id tokenization
        s = str(addr2).strip()
        s = s.replace(",", "")
        s = re.sub(r"\s+", "-", s)
        return s

    new_rows = []
    for key in eligible_keys:
        grp_idx = df.index[df["addressLine1"] == key]
        grp = df.loc[grp_idx]

        # Mark existing rows as apartment units
        df.loc[grp_idx, "propertyType"] = "Apartment"

        # First row becomes building template
        first = grp.iloc[0].copy()

        # Remove addressLine2 token from id, e.g.
        # "1-Brookside-Dr,-Apt-11,-Exeter,-NH-03833" -> "1-Brookside-Dr,-Exeter,-NH-03833"
        if "id" in first.index and "addressLine2" in first.index:
            addr2 = first["addressLine2"]
            if pd.notna(addr2) and str(addr2).strip():
                norm = _normalize_addr2_for_id(addr2)
                first["id"] = re.sub(rf",-{re.escape(norm)},", ",-", str(first["id"]))

        # Null fields for building record
        for col in ["addressLine2", "bedrooms", "bathrooms", "squareFootage"]:
            if col in first.index:
                first[col] = pd.NA

        # Set building property type
        first["propertyType"] = "Apartment building"

        # Align columns
        first = first.reindex(df.columns, fill_value=pd.NA)
        new_rows.append(first)

    if new_rows:
        new_rows_df = pd.DataFrame(new_rows, columns=df.columns)

        # Make all-NA columns explicitly match df dtypes in a safe way
        for col in new_rows_df.columns:
            if new_rows_df[col].isna().all():
                target = df[col].dtype
                # Float targets: use np.nan
                if pd.api.types.is_float_dtype(target):
                    new_rows_df[col] = np.nan
                    new_rows_df[col] = new_rows_df[col].astype(target)
                # Integer targets: use pandas nullable Int64
                elif pd.api.types.is_integer_dtype(target):
                    new_rows_df[col] = pd.Series([pd.NA] * len(new_rows_df), dtype="Int64")
                # Boolean targets: use pandas nullable boolean
                elif pd.api.types.is_bool_dtype(target):
                    new_rows_df[col] = pd.Series([pd.NA] * len(new_rows_df), dtype="boolean")
                # Datetime-like targets
                elif pd.api.types.is_datetime64_any_dtype(target):
                    new_rows_df[col] = pd.NaT
                    new_rows_df[col] = new_rows_df[col].astype(target)
                # Everything else: keep as object to avoid NA casting issues
                else:
                    new_rows_df[col] = new_rows_df[col].astype("object")

        df = pd.concat([df, new_rows_df], ignore_index=True)

    return df