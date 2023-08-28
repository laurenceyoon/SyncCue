import argparse
from twisted.internet import reactor
from .osc_server import OSCUDPServer
from .core.cue_detection import cue_detection_start
import subprocess

server = OSCUDPServer()


@server.add_handler("/start")
def handle_start(address, args=None):
    print(
        f"Received OSC message with {address}. Starting with arguments: {args, type(args)}"
    )
    cue_detection_start()


@server.add_handler("/stop")
def handle_stop(address, args=None):
    print(
        f"Received OSC message with {address}. Stopping with arguments: {args, type(args)}"
    )


@server.add_handler("/playback")
def handle_playback(address, args=None):
    print(
        f"Received OSC message with {address}. Playback with arguments: {args, type(args)}"
    )


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

    reactor.listenUDP(9999, server)
    reactor.run()
