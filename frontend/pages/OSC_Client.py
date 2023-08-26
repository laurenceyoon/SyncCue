import streamlit as st
from pythonosc import udp_client


def send_osc_msg(address, arguments):
    osc_client.send_message(address, arguments)
    st.text_area(
        label="Log message",
        value=f"Sent OSC Message.\nAddress: {OSC_SERVER_IP}:{OSC_SERVER_PORT}{address}, Arguments: {arguments}",
        disabled=True,
    )
    st.toast("Done!", icon="✅")


# ====================================

st.title("OSC Client")

# OSC Server IP and Port
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        OSC_SERVER_IP = st.text_input("OSC Server IP", "127.0.0.1")
    with col2:
        OSC_SERVER_PORT = int(st.text_input("OSC Server Port", 9999))
    osc_client = udp_client.SimpleUDPClient(OSC_SERVER_IP, OSC_SERVER_PORT)


# Send OSC Message
with st.container():
    st.subheader("Send OSC Message")
    st.caption("Choose an OSC message to send:")

    # OSC Message List
    with st.expander("/start"):
        address = st.text_input("address", key="start_address", value="/start")
        arguments = st.text_input("arguments", key="start_arguments", value="0") or None
        if st.button("Send", key="start_send", use_container_width=True):
            send_osc_msg(address, arguments)

    with st.expander("/stop"):
        address = st.text_input("address", key="stop_address", value="/stop")
        arguments = (
            st.text_input("arguments", key="stop_arguments", value="[1]") or None
        )
        if st.button("Send", key="stop_send", use_container_width=True):
            send_osc_msg(address, arguments)

    with st.expander("/playback"):
        address = st.text_input("address", key="playback_address", value="/playback")
        arguments = (
            st.text_input("arguments", key="playback_arguments", value="") or None
        )
        if st.button("Send", key="playback_send", use_container_width=True):
            send_osc_msg(address, arguments)
