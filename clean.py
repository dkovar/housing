# clean.py
import pandas as pd
import ast
import numpy as np
import re

def safe_parse(value):
    """
    Safely parse a string to a Python object using literal_eval if it looks like a dict.
    Returns an empty dict on failure or if value is NaN/invalid.
    """
    try:
        if pd.notna(value) and isinstance(value, str) and value.strip().startswith("{"):
            return ast.literal_eval(value)
    except Exception:
        pass
    return {}

def clean_housing_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans up housing dataset:
      - Parses certain columns containing dict-like strings
      - Normalizes property types
      - Fills missing numeric values for bedrooms, bathrooms, yearBuilt
    """

    # Parse nested dict columns safely
    for col in ["features", "taxAssessments", "propertyTaxes", "owner"]:
        if col in df.columns:
            df[col] = df[col].apply(safe_parse)

    # Normalize propertyType
    df["propertyType"] = df["propertyType"].fillna("").apply(lambda x: x.strip() if isinstance(x, str) else "")
    df["propertyType"] = df["propertyType"].replace("", "Unknown")

    # Replace missing numeric fields
    df["bedrooms"] = pd.to_numeric(df["bedrooms"], errors="coerce").fillna(0).astype(int)
    df["bathrooms"] = pd.to_numeric(df["bathrooms"], errors="coerce").fillna(0)
    df["yearBuilt"] = pd.to_numeric(df["yearBuilt"], errors="coerce").fillna(1600).astype(int)

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
        df.loc[grp_idx, "propertyType"] = "Apartment unit"

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