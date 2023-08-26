import streamlit as st
import pandas as pd

st.title("Database Viewer")

with st.container():
    st.markdown("## Table `pieces`")
    df = pd.DataFrame(
        [
            {"title": "Haydn", "midi_path": "./resources/a.midi"},
            {"title": "Schubert", "midi_path": "./resources/b.midi"},
            {"title": "Liszt", "midi_path": "./resources/c.midi"},
        ]
    )
    edited_df = st.data_editor(df, width=1000)
