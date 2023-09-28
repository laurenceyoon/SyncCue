import streamlit as st
import pandas as pd
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

st.title("Candidate Server (8888)")

# Basic Info
with st.container():
    st.subheader("Basic OSC Configuration")
    col1, col2 = st.columns(2)
    with col1:
        OSC_SERVER_IP = st.text_input("OSC Server IP", "127.0.0.1")
    with col2:
        OSC_SERVER_PORT = int(st.text_input("OSC Server Port", 8888))

df = pd.DataFrame(
    {
        "ID": ["0", "1-0", "1-1", "1-2", "2"],
        "Title": ['반짝반짝 작은별', '시네마천국 파트 0', '시네마천국 파트 1', \
            '시네마천국 파트 2', '왕벌의 비행']
    }
)
st.dataframe(
    df,
    column_config={"name": "ID"},
    hide_index = True
)

# OSC In
with st.container():
    st.subheader("OSC In")
    osc_client = udp_client.SimpleUDPClient(OSC_SERVER_IP, OSC_SERVER_PORT)

    with st.expander("/playback"):
        address = st.text_input("Token", key="playback_address", value="/playback")
        arguments = (
            st.text_input("ID", key="playback_arguments", value="1-2") or None
        )
        if st.button("Send", key="playback_send", use_container_width=True):
            send_osc_msg(address, arguments)
