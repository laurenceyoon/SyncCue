import streamlit as st


def read_file(file):
    with open(file, "r", encoding="utf-8") as f:
        content = f.read()
        return content


readme_content = read_file("README.md")
st.markdown(readme_content, unsafe_allow_html=True)
