import streamlit as st
import pandas as pd
import time

from app.database import get_piece_list, insert_piece, update_piece

st.title("Database Viewer")

# session state setup
if "last_clicked" not in st.session_state:
    st.session_state.last_clicked = None
if "selected_row" not in st.session_state:
    st.session_state.selected_row = None

with st.container():
    st.markdown("### Table `pieces`")
    pieces = get_piece_list()
    pieces_df = pd.DataFrame([piece.to_mongo().to_dict() for piece in pieces])
    pieces_df.insert(0, "select", False)
    edited_df = st.data_editor(pieces_df, width=800)

    selected_rows = edited_df[edited_df["select"] == True]
    if not selected_rows.empty:
        selected_row = selected_rows.iloc[-1]
        st.session_state.selected_row = selected_row
        st.table(selected_row)
        if st.button("Edit"):
            st.session_state.last_clicked = "Edit"

    if (
        st.session_state.last_clicked == "Edit"
        and st.session_state.selected_row is not None
    ):
        with st.expander("Edit Piece", expanded=True):
            edit_title = st.text_input("Title", value=selected_row["title"])
            edit_composer = st.text_input("Composer", value=selected_row["composer"])
            edit_midi_path = st.text_input("MIDI Path", value=selected_row["midi_path"])
            edit_audio_path = st.text_input(
                "Audio Path", value=selected_row["audio_path"]
            )

            if st.button("Update Piece"):
                updated_piece = update_piece(
                    st.session_state.selected_row["_id"],
                    edit_title,
                    edit_composer,
                    edit_midi_path,
                    edit_audio_path,
                )
                st.success(f"Updated piece with ID {updated_piece.title}!")
                st.session_state.last_clicked = None
                st.session_state.selected_row = None
                time.sleep(2)
                st.experimental_rerun()

    if st.button("Add"):
        st.session_state.last_clicked = "Add"

    if st.session_state.last_clicked == "Add":
        with st.expander("Add New Piece", expanded=True):
            new_title = st.text_input("Title", key="new_title")
            new_composer = st.text_input("Composer")
            new_midi_path = st.text_input("MIDI Path")
            new_audio_path = st.text_input("Audio Path")
            if st.button("Add Piece"):
                new_piece = insert_piece(
                    new_title, new_composer, new_midi_path, new_audio_path
                )
                st.success(f"Added new piece with ID {new_piece.id}!")
                st.session_state.last_clicked = None
