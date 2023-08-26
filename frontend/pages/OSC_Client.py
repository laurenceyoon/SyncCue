import streamlit as st
from pythonosc import udp_client

st.title("OSC Client")

# OSC Server IP and Port
col1, col2 = st.columns(2)
with col1:
    OSC_SERVER_IP = st.text_input("OSC Server IP", "127.0.0.1")
with col2:
    OSC_SERVER_PORT = int(st.text_input("OSC Server Port", 9999))

osc_client = udp_client.SimpleUDPClient(OSC_SERVER_IP, OSC_SERVER_PORT)

with st.container():
    st.subheader("Send OSC Message")
    st.caption("Choose an OSC message to send:")

    # OSC Message List
    if st.button("Send /play", key="play", use_container_width=True):
        osc_client.send_message("/play", None)
        sent_message = "/play"

    if st.button("Send /stop", key="stop", use_container_width=True):
        osc_client.send_message("/stop", None)
        sent_message = "/stop"

    if st.button("Send /playback", key="playback", use_container_width=True):
        osc_client.send_message("/playback", None)
        sent_message = "/playback"

    if "sent_message" in locals():
        st.text_area(
            label="Log message",
            value=f"Sent OSC Message.\nAddress: {OSC_SERVER_IP}:{OSC_SERVER_PORT}{sent_message}",
            disabled=True,
        )
        st.toast("Done!", icon="✅")
