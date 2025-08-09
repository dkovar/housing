import pandas as pd
import ast
import streamlit as st
import os

def load_data(path):
    if not os.path.exists(path):
        st.error(f"❌ The file '{path}' was not found.")
        st.stop()

    try:
        df = pd.read_csv(path)
    except Exception as e:
        st.error(f"❌ Failed to read '{path}': {e}")
        st.stop()

    for col in ["features", "taxAssessments", "propertyTaxes", "owner"]:
        def safe_parse(x):
            try:
                return ast.literal_eval(x) if pd.notna(x) and isinstance(x, str) and x.strip().startswith("{") else {}
            except Exception:
                return {}
        df[col] = df[col].apply(safe_parse)

    df["propertyType"] = df["propertyType"].fillna("").apply(lambda x: x.strip() if isinstance(x, str) else "")
    df["propertyType"] = df["propertyType"].replace("", "Unknown")

    df["bedrooms"] = pd.to_numeric(df["bedrooms"], errors="coerce").fillna(0).astype(int)
    df["bathrooms"] = pd.to_numeric(df["bathrooms"], errors="coerce").fillna(0)
    df["yearBuilt"] = pd.to_numeric(df["yearBuilt"], errors="coerce").fillna(1600).astype(int)

    return df