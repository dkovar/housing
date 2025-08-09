# pages/todo_readonly.py
import streamlit as st
import os

TODO_PATH = "todo.md"  # change to whatever filename you want

def render():
    # Optional: let user refresh after you edit the file externally
    st.button("Refresh")

    if not os.path.exists(TODO_PATH):
        st.error(f"'{TODO_PATH}' not found in the current directory.")
        st.info("Create a file named 'todo.md' with your tasks, then click Refresh.")
        return

    try:
        # If you ever hit encoding issues, add encoding='utf-8' or 'latin-1'
        with open(TODO_PATH, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        st.error(f"Couldn't read '{TODO_PATH}': {e}")
        return

    # Render as Markdown (wrapped text, headings, numbered lists, etc.)
    st.markdown(content)