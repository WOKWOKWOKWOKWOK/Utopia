import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# Read the local index.html file from the repository
html_file = Path("index.html")

if html_file.exists():
    html_content = html_file.read_text(encoding="utf-8")
    components.html(html_content, height=900, scrolling=True)
else:
    st.error("No index.html file found in the root directory.")
