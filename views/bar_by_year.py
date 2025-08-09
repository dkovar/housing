import streamlit as st

def render(filtered_df):
    st.subheader("Properties Built by Year and Type")
    max_year = filtered_df["yearBuilt"].max()
    min_year = filtered_df["yearBuilt"].min()
    num_years = st.slider("Show properties built in the last N years:", 1, max_year - min_year, 50)
    year_threshold = max_year - num_years
    year_df = filtered_df[filtered_df["yearBuilt"] >= year_threshold]
    year_type_counts = year_df.groupby(["yearBuilt", "propertyType"]).size().unstack(fill_value=0)
    st.bar_chart(year_type_counts)