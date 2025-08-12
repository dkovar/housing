import streamlit as st
from data_loader import load_data
from filters import apply_filters
from views import (
    raw_data,
    pie_chart,
    bar_by_year,
    other_charts,
    map_view,
    about,
    background,
    todo,
    data
)
from clean import clean_housing_data

st.set_page_config(layout="wide")
st.title("🏠 Housing Data Explorer")

# Pages list (Landing first)
PAGES = [
    "Landing",
    "Raw Data",
    "Property Type Pie Chart",
    "Property Type by Year Built",
    "Other Charts",
    "Map View",
    "About",
    "Background",
]

# Keep current page in session
if "page" not in st.session_state:
    st.session_state.page = "Landing"

# Sidebar nav (you can keep filters above or below as you prefer)
st.sidebar.title("Navigation")
selected = st.sidebar.radio("Select a section", PAGES, index=PAGES.index(st.session_state.page))
if selected != st.session_state.page:
    navigate_to(selected)

# Route
page = st.session_state.page
if page == "Landing":
    landing.render(navigate_to, PAGES)
elif page == "Raw Data":
    raw_data.render(filtered_df)
elif page == "Property Type Pie Chart":
    pie_chart.render(filtered_df)
elif page == "Property Type by Year Built":
    bar_by_year.render(filtered_df)
elif page == "Other Charts":
    other_charts.render(filtered_df)
elif page == "Map View":
    map_view.render(filtered_df)
elif page == "About":
    about.render()
elif page == "Background":
    background.render()
