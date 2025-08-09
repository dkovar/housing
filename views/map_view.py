import streamlit as st

def render(filtered_df):
    st.subheader("Property Locations")
    if "latitude" in filtered_df.columns and "longitude" in filtered_df.columns:
        st.map(filtered_df[["latitude", "longitude"]].dropna())
    else:
        st.warning("Latitude and Longitude data not available.")