import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd

def render(filtered_df):
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
        st.info("No property tax data available.")