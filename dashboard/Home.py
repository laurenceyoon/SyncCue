import streamlit as st
from pythonosc import udp_client
import sys
import os
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.getenv("PYTHONPATH"))


def send_osc_msg(address, arguments=""):
    osc_client.send_message(address, arguments)
    st.text_area(
        label="Log message",
        value=f"Sent OSC Message.\nAddress: {OSC_CLIENT_IP}:{OSC_CLIENT_PORT}{address}, Arguments: {arguments}",
        disabled=True,
    )
    st.toast("Done!", icon="✅")


st.title("SyncCue")

# Basic Info
with st.container():
    st.subheader("[MACLab] KAIST AI Pianist with 최나경")
    col1, col2 = st.columns(2)
    with col1:
        OSC_CLIENT_IP = st.text_input("OSC Client IP", "192.168.0.20")
    with col2:
        OSC_CLIENT_PORT = int(st.text_input("OSC Client Port", 9999))

# OSC In
with st.container():
    st.subheader("OSC In")
    osc_client = udp_client.SimpleUDPClient(OSC_CLIENT_IP, OSC_CLIENT_PORT)
    st.caption("Choose an OSC message to send:")

    # OSC Message List

    with st.expander("/intro"):  # Intro (Call the drones on the stage)
        address = st.text_input("address", key="intro_address", value="/intro")
        if st.button("Send", key="intro_send", use_container_width=True):
            send_osc_msg(address)

    with st.expander("/start"):
        address = st.text_input("address", key="start_address", value="/start")
        arguments = st.text_input("arguments", key="start_arguments", value="1") or None
        if st.button("Send", key="start_send", use_container_width=True):
            send_osc_msg(address, arguments)

    with st.expander("/stop"):
        address = st.text_input("address", key="stop_address", value="/stop")
        arguments = st.text_input("arguments", key="stop_arguments", value="1") or None
        if st.button("Send", key="stop_send", use_container_width=True):
            send_osc_msg(address, arguments)

    with st.expander("/playback"):
        address = st.text_input("address", key="playback_address", value="/playback")
        arguments = (
            st.text_input("arguments", key="playback_arguments", value="0") or None
        )
        if st.button("Send", key="playback_send", use_container_width=True):
            send_osc_msg(address, arguments)

    with st.expander("/outro"):  # Outro (Finale; Firework)
        address = st.text_input("address", key="outro_address", value="/outro")
        if st.button("Send", key="outro_send", use_container_width=True):
            send_osc_msg(address)
