import streamlit as st
import pandas as pd

def make_summary_series(df: pd.DataFrame) -> pd.Series:
    data = {
        "Total Properties": len(df),
        "Year Range": f"{df['yearBuilt'].min()} – {df['yearBuilt'].max()}",
    }
    # Add "<Type> Units" counts
    type_counts = df["propertyType"].value_counts(dropna=False).to_dict()
    for prop_type, count in type_counts.items():
        data[f"{prop_type} Units"] = int(count)
    return pd.Series(data)

def render(df_before, df_after, filtered_df):
    st.subheader("Data issues")
    st.markdown("""
- Records with an invalid or missing 'Year Built' value were assigned the year 1600.
- Similarly, records with an unknown number of bedrooms or bathrooms have those values set to 0.
- Apartment data is problematic. There is one record for the building itself with that includes the total number of bathrooms but not much else. Then there are records for each apartment with no other useful data. We can assume that each apartment belongs to the building at the same address, and assume it is rented rather than owned.
- Condos are similar to apartments in that there are records for each unit as well as the building. This means that, without some careful data cleaning, the number of condos is the number of condo units. The fix is likely to create a new record for condo buildings and clean the data appropriately.
- A number of records include just an address with no additional data. These are most often apartments
- There is no clean way to identify an ADU. It might be possible to identify ADUs through analysis.
""")

    # Build per-stage summaries as Series
    s_before   = make_summary_series(df_before).rename("Before Cleaning")
    s_after    = make_summary_series(df_after).rename("After Cleaning")
    s_filtered = make_summary_series(filtered_df).rename("After Filtering")

    # Combine into one vertical table; missing entries become NaN (null)
    combined = pd.concat([s_before, s_after, s_filtered], axis=1)

    # Optional: order rows so headline metrics come first
    head = ["Total Properties", "Year Range"]
    rest = [idx for idx in combined.index if idx not in head]
    combined = combined.reindex(head + sorted(rest, key=str.lower))

    st.subheader("Summary of Data — Before/After Cleaning and Filtering")
    st.dataframe(combined)

    st.subheader("Filtered Housing Data")
    st.dataframe(filtered_df)
    
    # --- Top 5 groups of Unknown records (by addressLine1) ---
    st.subheader("Top 5 Groups of Unknown Records")

    if {"propertyType", "addressLine1", "addressLine2"}.issubset(filtered_df.columns):
        unknown = filtered_df[filtered_df["propertyType"] == "Unknown"].copy()

        if unknown.empty:
            st.info("No Unknown records in the current filtered data.")
        else:
            counts = (
                unknown.groupby("addressLine1", dropna=False)
                       .size()
                       .sort_values(ascending=False)
            )
            top5_addresses = counts.head(5).index

            top5_rows = (
                unknown[unknown["addressLine1"].isin(top5_addresses)]
                .loc[:, ["addressLine1", "addressLine2"]]
                .sort_values(by=["addressLine1", "addressLine2"], kind="mergesort")
            )

            st.dataframe(top5_rows, use_container_width=True)
    else:
        st.warning("Required columns not found to compute Unknown groups.")

