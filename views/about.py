import streamlit as st

def render():
    st.title("About This App")
    st.markdown("""I built this application to explore housing stock and housing ownership in Exeter, NH. 
This is an independent project and in no way should be considered as representing anyone's opinions other than my own.

The application is a work in progress, the data is "noisy", and assumptions or outright errors may be present in the code. 
Use the data and analysis at your own risk. 

The data is purchased from RentCast. Any errors in the presentation or analysis are mine. RentCast has been a pleasure to work with.""")