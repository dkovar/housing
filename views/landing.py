# views/landing.py
import streamlit as st
from pathlib import Path

MD_PATH = Path("views/landing.md")

def render(navigate, page_labels):
    st.title("Welcome")

    # Read landing markdown
    if not MD_PATH.exists():
        st.error(f"Missing file: {MD_PATH}. Create it to show landing content.")
    else:
        try:
            content = MD_PATH.read_text(encoding="utf-8")
            st.markdown(content)
        except Exception as e:
            st.error(f"Couldn't read {MD_PATH}: {e}")

    st.divider()
    st.subheader("Go to a section")

    # Buttons for each page (skip Landing itself)
    cols = st.columns(3)
    i = 0
    for label in page_labels:
        if label == "Landing":
            continue
        with cols[i % 3]:
            if st.button(label, key=f"landing_btn_{label}"):
                navigate(label)
        i += 1
