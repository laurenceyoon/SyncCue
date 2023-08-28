import os
import sys

import streamlit as st
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.getenv("PYTHONPATH"))


def read_file(file):
    with open(file, "r", encoding="utf-8") as f:
        content = f.read()
        return content


readme_content = read_file("README.md")
st.markdown(readme_content, unsafe_allow_html=True)
