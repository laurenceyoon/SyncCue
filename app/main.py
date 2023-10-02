import argparse
import asyncio
import subprocess

from twisted.internet import asyncioreactor

from app.core.helpers import (
    all_stop_playing,
    cue_detection_start_for_piece,
    playback_start_for_piece,
)

asyncioreactor.install()
from twisted.internet import reactor

from app.config import OSC_SERVER_PORT
from app.osc_client import send_osc_intro, send_osc_outro
from app.osc_server import server


async def run_in_background(func, *args, **kwargs):
    return await asyncio.to_thread(func, *args, **kwargs)


@server.add_handler("/start")
async def handle_start(address, args):
    await run_in_background(cue_detection_start_for_piece, args)


@server.add_handler("/playback")
async def handle_playback(address, args=None):
    await run_in_background(playback_start_for_piece, args)


@server.add_handler("/stop")
async def handle_stop(address, args=None):
    all_stop_playing()


@server.add_handler("/intro")
async def handle_intro(address, args=None):
    print("Intro Start; Command Unity to Start the INTRO Animation.")
    send_osc_intro()


@server.add_handler("/outro")
async def handle_intro(address, args=None):
    print("Outro Start; Command Unity to Start the OUTRO Animation.")
    send_osc_outro()


def run_streamlit_app():
    subprocess.Popen(["streamlit", "run", "dashboard/Home.py"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--no-dashboard", action="store_true", help="Run server without dashboard"
    )
    args = parser.parse_args()

    if not args.no_dashboard:
        run_streamlit_app()

    reactor.listenUDP(OSC_SERVER_PORT, server)
    reactor.run()
