import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import ConnectionPatch
import ast
import os

st.set_page_config(layout="wide")
st.title("🏠 Housing Data Explorer")


# Read from static file
csv_path = "./table.csv"

if not os.path.exists(csv_path):
    st.error(f"❌ The file '{csv_path}' was not found in the current directory.")
    st.stop()

try:
    df = pd.read_csv(csv_path)
except Exception as e:
    st.error(f"❌ Failed to read '{csv_path}': {e}")
    st.stop()

# Parse nested dict columns safely
for col in ["features", "taxAssessments", "propertyTaxes", "owner"]:
    if col in df.columns:
        def safe_parse(x):
            try:
                return ast.literal_eval(x) if pd.notna(x) and isinstance(x, str) and x.strip().startswith("{") else {}
            except Exception:
                return {}
        df[col] = df[col].apply(safe_parse)

# Normalize propertyType
df["propertyType"] = df["propertyType"].fillna("").apply(lambda x: x.strip() if isinstance(x, str) else "")
df["propertyType"] = df["propertyType"].replace("", "Unknown")

# Replace missing numeric fields
df["bedrooms"] = pd.to_numeric(df["bedrooms"], errors="coerce").fillna(0).astype(int)
df["bathrooms"] = pd.to_numeric(df["bathrooms"], errors="coerce").fillna(0)
df["yearBuilt"] = pd.to_numeric(df["yearBuilt"], errors="coerce").fillna(1600).astype(int)

# --- Sidebar Filters ---
st.sidebar.header("🔍 Filters")

# Property type checkboxes
st.sidebar.markdown("### Property Types")
all_types = sorted(df["propertyType"].unique())
selected_types = [
    t for t in all_types if st.sidebar.checkbox(t, value=True, key=f"ptype_{t}")
]

# Bedrooms, Bathrooms, Year Built sliders with fixed ranges
bedrooms = st.sidebar.slider("Bedrooms", 0, 10, (0, 10))
bathrooms = st.sidebar.slider("Bathrooms", 0.0, 10.0, (0.0, 10.0))
year_range = st.sidebar.slider("Year Built", 1600, 2025, (1600, 2025))

# Filter the data
filtered_df = df[
    (df["propertyType"].isin(selected_types)) &
    (df["bedrooms"].between(bedrooms[0], bedrooms[1])) &
    (df["bathrooms"].between(bathrooms[0], bathrooms[1])) &
    (df["yearBuilt"].between(year_range[0], year_range[1]))
]

# --- Tabs ---
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📊 Raw Data",
    "🥧 Property Type Pie Chart",
    "🏗️ Type by Year Built",
    "📈 Other Charts",
    "🗺️ Map View",
    "ℹ️ About",
    "ℹ️ Backstory"

])

# --- Tab 1: Raw Data and Summary ---
with tab1:
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

    summary_df = pd.DataFrame(summary_data)
    st.dataframe(summary_df)

    st.subheader("Filtered Housing Data")
    st.dataframe(filtered_df)

# --- Tab 2: Property Type Pie Chart ---
with tab2:
    st.subheader("Distribution of Property Types")
    type_counts = filtered_df["propertyType"].value_counts()
    labels = type_counts.index.tolist()
    sizes = type_counts.values
    total = sizes.sum()

    fig, ax = plt.subplots(figsize=(8, 6))
    wedges, _ = ax.pie(sizes, startangle=90, radius=1.2)
    ax.axis('equal')

    # Identify small wedges for outside labeling
    small_wedges = []
    small_angles = []
    small_labels = []
    small_percents = []

    for i, (wedge, label, size) in enumerate(zip(wedges, labels, sizes)):
        percent = size / total * 100
        angle = (wedge.theta2 + wedge.theta1) / 2
        x = np.cos(np.deg2rad(angle))
        y = np.sin(np.deg2rad(angle))

        if percent >= 10:
            # Inline label
            ax.text(x * 0.8, y * 0.8, f"{label}\n{percent:.1f}%", ha='center', va='center', fontsize=9)
        else:
            # Collect small wedge data to place later
            small_wedges.append((x, y))
            small_angles.append(angle)
            small_labels.append(label)
            small_percents.append(percent)

    # Dynamically assign y-positions for small labels
    if small_wedges:
        offset_ys = np.linspace(1, -1, len(small_wedges))
        for (x, y), angle, label, percent, label_y in zip(small_wedges, small_angles, small_labels, small_percents, offset_ys):
            label_x = 1.6 * np.sign(x)

            # Draw arrow
            con = ConnectionPatch(
                xyA=(x, y), coordsA=ax.transData,
                xyB=(label_x, label_y), coordsB=ax.transData,
                arrowstyle='-', lw=1, color='gray'
            )
            ax.add_artist(con)

            # Draw label
            ax.text(label_x, label_y,
                    f"{label} ({percent:.1f}%)",
                    ha='left' if x >= 0 else 'right',
                    va='center',
                    fontsize=9)

    st.pyplot(fig)


# --- Tab 3: Property Type by Year Built ---
with tab3:
    st.subheader("Properties Built by Year and Type")
    max_year = filtered_df["yearBuilt"].max()
    min_year = filtered_df["yearBuilt"].min()
    num_years = st.slider("Show properties built in the last N years:", 1, max_year - min_year, 50)
    year_threshold = max_year - num_years
    year_df = filtered_df[filtered_df["yearBuilt"] >= year_threshold]
    year_type_counts = year_df.groupby(["yearBuilt", "propertyType"]).size().unstack(fill_value=0)
    st.bar_chart(year_type_counts)

# --- Tab 4: Other Charts ---
with tab4:
    st.subheader("Distribution of Bedrooms and Bathrooms")
    fig, axs = plt.subplots(1, 2, figsize=(12, 4))
    filtered_df["bedrooms"].value_counts().sort_index().plot(kind='bar', ax=axs[0], title="Bedrooms")
    filtered_df["bathrooms"].value_counts().sort_index().plot(kind='bar', ax=axs[1], title="Bathrooms")
    st.pyplot(fig)

    st.subheader("Square Footage vs. Year Built")
    st.scatter_chart(filtered_df[["yearBuilt", "squareFootage"]])

    st.subheader("Average Property Tax by Year")
    def extract_tax_by_year(taxes):
        return {str(y): t['total'] for y, t in taxes.items()} if isinstance(taxes, dict) else {}

    tax_df = pd.DataFrame(filtered_df["propertyTaxes"].apply(extract_tax_by_year).tolist())
    tax_mean = tax_df.mean().dropna()
    if not tax_mean.empty:
        st.bar_chart(tax_mean)
    else:
        st.info("No property tax data available for selected filters.")

# --- Tab 5: Map View ---
with tab5:
    st.subheader("Property Locations")
    if "latitude" in filtered_df.columns and "longitude" in filtered_df.columns:
        st.map(filtered_df[["latitude", "longitude"]].dropna())
    else:
        st.warning("Latitude and Longitude data not available.")
        
with tab6:
    st.title("About This App")

    st.markdown("""I built this application to explore housing stock and housing ownership in Exeter, NH. This is an independent project and in no way should be considered as representing anyone's opinions other than my own.

The application is a work in progress, the data is "noisy", and assumptions or outright errors may be present in the code. Use the data and analysis at your own risk. 

The data is purchased from RentCast. Any errors in the presentation or analysis are mine. RentCast has been a pleasure to work with.""")

with tab7:
    st.title("Background")
    st.subheader("Why?")

    st.markdown("""This started as an effort to educate myself about a local housing crisis and I suspect it will be part of an ongoing effort to educate myself about housing in general.""")

    st.subheader("Data access, data quality")

    st.markdown("""I thought I could just walk into the Town's offices, or go to their web site, and find detailed data about the housing stock in town. How many condos, single family dwellings, town houses, etc exist? When were they built? Are they rented or owner occupied? And, what housing has been built, is being planned, or is under construction? I hoped for raw (CSV, Excel) data but would have been happy with detailed, structured PDFs.

The assessor's office doesn't have any data at this level of detail. The best document is a yearly filing with the state. The planning board submits a yearly, high level report. For better detail I was told to read the meeting minutes. These exist but other than following Robert's Rules of Order they lack the necessary structure required to programatically analyze them. (Using AI to summarize the reports would potentially introduce errors, compounding the problem.)""")

    st.subheader("Tangent - Engagement and Town Support")

    st.markdown("""Please do not take any of this work as an indictment or criticism of the Town's government, boards, committees, staff, or volunteers. I live here, I am a big fan of everyone involved in running the Town, and I think that we collectively are doing an excellent job. Where we fail, or don't do as well as we might, we are open to feedback and make every effort to improve.

I am on several committees, including the Communications Committee. I deeply appreciate the opportunity to gain experience as an active participant in local government. This application represents my effort to both educate myself and to improve our ability to communicate with the community on the complex issue that is housing.""")

    st.subheader("Government Transparency")

    st.markdown("""Technically, the Town complies with all local, state, and Federal regulations and laws about transparency and data access. My issue isn't with the Town, it is with the fact that the definition of "transparency" hasn't kept pace with technology and society. We are data driven, and good decisions depend in part on access to good data (and we can discuss the defition of "good data" elsewhere.) Government transparency in this day and age requires addressing two sub-issues:

1) The data exists somewhere in a local, state, or commercial database but it is not available to the public. A report based on the data is legally sufficient. (And the fact that I need to pay a commercial data aggregator for access to data collected by the government is yet another issue.)

A requirement to make certain classes of data available in raw form suitable for analysis would address this issue.

2) The data isn't collected and stored in a form that lends itself to sharing or later analysis. The planning board knows everything possible about proposed, approved, and denied residential construction but that knowledge is likely in the form of written proposals, architectural drawings, and verbal communications. 

If there was a requirement for all building proposals to include critical data in a standardized, structured form using an Excel template then the data could easily be collected and shared.""")

    st.subheader("So, This Application")

    st.markdown("""This is intended to educate myself and to spark discussions so that we as a community can come together with a shared understanding of what our housing looks like and inform discussions about our desired collective future.""")

