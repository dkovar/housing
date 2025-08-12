import streamlit as st
from data_loader import load_data
from filters import apply_filters
from views import (
    landing,
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

data_path = "./table.csv"

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

@st.cache_data
def load_and_clean_data(path):
    df = load_data(path)
    df = clean_housing_data(df)
    return df

df = load_and_clean_data(data_path)

# Keep current page in session
if "page" not in st.session_state:
    st.session_state.page = "Landing"

def navigate_to(page_label: str):
    st.session_state.page = page_label
    # Streamlit >= 1.27
    st.rerun()
    
# Sidebar nav (you can keep filters above or below as you prefer)
st.sidebar.title("Navigation")
selected = st.sidebar.radio("Select a section", PAGES, index=PAGES.index(st.session_state.page))
if selected != st.session_state.page:
    navigate_to(selected)

filtered_df = apply_filters(df)

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
    

