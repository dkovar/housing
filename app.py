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

st.set_page_config(layout="wide")
st.title("🏠 Housing Data Explorer")

df = load_data("table.csv")
df = clean_housing_data(df)


st.sidebar.title("Navigation")
page = st.sidebar.radio("Select a section", [
    "Raw Data",
    "Property Type Pie Chart",
    "Property Type by Year Built",
    "Other Charts",
    "Map View",
    "About",
    "Background",
    "To Do",
    "Data"
])

filtered_df = apply_filters(df)

if page == "Raw Data":
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
elif page == "To Do":
    todo.render()
elif page == "Data":
    data.render()
