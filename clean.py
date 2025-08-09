# clean.py
import pandas as pd
import ast

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