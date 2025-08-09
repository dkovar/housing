import streamlit as st
import pandas as pd

def render(filtered_df):
    st.subheader("Data issues")
    st.markdown("""
    - Records with an invalid or missing 'Year Built' value were assigned the year 1600.
    - Similarly, records with an unknown number of bedrooms or bathrooms have those values set to 0.
    - Apartment data is problematic. There is one record for the building itself with that includes the total number of bathrooms but not much else. Then there are records for each apartment with no other useful data. We can assume that each apartment belongs to the building at the same address, and assume it is rented rather than owned.
    - Condos are similar to apartments in that there are records for each unit as well as the building. This means that, without some careful data cleaning, the number of condos is the number of condo units. The fix is likely to create a new record for condo buildings and clean the data appropriately.
    - A number of records include just an address with no additional data. These are most often apartments
    - There is no clean way to identify an ADU. It might be possible to identify ADUs through analysis.""")
    
    st.subheader("Summary of Filtered Data")
    summary_data = {
        "Total Properties": [len(filtered_df)],
        "Year Range": [f"{filtered_df['yearBuilt'].min()} – {filtered_df['yearBuilt'].max()}"],
    }

    type_counts = filtered_df["propertyType"].value_counts().to_dict()
    for prop_type, count in type_counts.items():
        summary_data[f"{prop_type} Units"] = [count]

    st.dataframe(pd.DataFrame(summary_data))

    st.subheader("Filtered Housing Data")
    st.dataframe(filtered_df)