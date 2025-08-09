import streamlit as st

def render():
    st.title("About This App")
    st.markdown("""I built this application to explore housing stock and housing ownership in Exeter, NH. 
This is an independent project and in no way should be considered as representing anyone's opinions other than my own.

I discuss challenges that I face in this process using Exeter NH as an example. It is very important to note that the Town staff, Select Board, and various committees are incredibly easy to work with. They are not the barrier, entropy, regulations, laws, culture, and other factors create the biggest challenges that we must overcome.

The application is a work in progress, the data is "noisy", and assumptions or outright errors may be present in the code. 
Use the data and analysis at your own risk. 

Please direct any questions, comments, or suggestions to exploringhousing@gmail.com""")