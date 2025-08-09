import streamlit as st

def apply_filters(df):
    st.sidebar.header("🔍 Filters")
    st.sidebar.markdown("### Property Types")
    all_types = sorted(df["propertyType"].unique())
    selected_types = [t for t in all_types if st.sidebar.checkbox(t, value=True, key=f"ptype_{t}")]

    bedrooms = st.sidebar.slider("Bedrooms", 0, 10, (0, 10))
    bathrooms = st.sidebar.slider("Bathrooms", 0.0, 10.0, (0.0, 10.0))
    year_range = st.sidebar.slider("Year Built", 1600, 2025, (1600, 2025))

    return df[
        (df["propertyType"].isin(selected_types)) &
        (df["bedrooms"].between(bedrooms[0], bedrooms[1])) &
        (df["bathrooms"].between(bathrooms[0], bathrooms[1])) &
        (df["yearBuilt"].between(year_range[0], year_range[1]))
    ]