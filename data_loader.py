import pandas as pd
import ast
import streamlit as st
import os

def load_data(path):
    if not os.path.exists(path):
        st.error(f"❌ The file '{path}' was not found.")
        st.stop()

    try:
        df = pd.read_csv(path)
    except Exception as e:
        st.error(f"❌ Failed to read '{path}': {e}")
        st.stop()
        
    return df