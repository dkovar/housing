import streamlit as st
import pandas as pd

def render(filtered_df: pd.DataFrame, base_df: pd.DataFrame | None = None):
    st.subheader("Properties Built by Year and Type")

    if base_df is None:
        base_df = filtered_df

    if "yearBuilt" not in base_df.columns or "propertyType" not in base_df.columns:
        st.warning("Required columns not found: yearBuilt and/or propertyType.")
        return

    # ---- Lock slider bounds using base_df (not filtered_df)
    base_years = pd.to_numeric(base_df["yearBuilt"], errors="coerce").dropna()
    if base_years.empty:
        st.info("No yearBuilt data available.")
        return

    max_year = int(base_years.max())
    min_year = int(base_years.min())

    span = max_year - min_year
    if span <= 0:
        span = 1  # keep slider valid

    num_years = st.slider(
        "Show properties built in the last N years:",
        min_value=1,
        max_value=int(span),
        value=min(50, int(span)),
        step=1,
    )

    year_threshold = max_year - num_years

    # ---- Apply slider threshold to the *filtered* data
    df = filtered_df.copy()
    df["_yearBuilt_num"] = pd.to_numeric(df["yearBuilt"], errors="coerce")

    df = df[df["_yearBuilt_num"].notna() & (df["_yearBuilt_num"] >= year_threshold)]
    if df.empty:
        st.info("No records in that year range for the current filters.")
        return

    # ---- Bucket years < 1900 into "pre-1900"
    df["_yearBucket"] = df["_yearBuilt_num"].apply(lambda y: "pre-1900" if y < 1900 else int(y))

    # Group counts
    year_type_counts = (
        df.groupby(["_yearBucket", "propertyType"], dropna=False)
          .size()
          .unstack(fill_value=0)
    )

    # Sort index so "pre-1900" comes first, then numeric years ascending
    def _bucket_sort_key(v):
        if v == "pre-1900":
            return (0, 0)
        return (1, int(v))

    year_type_counts = year_type_counts.loc[sorted(year_type_counts.index, key=_bucket_sort_key)]

    st.bar_chart(year_type_counts)

