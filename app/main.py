import argparse
from twisted.internet import reactor
from .osc_server import OSCUDPServer
import subprocess


server = OSCUDPServer()


@server.add_handler("/start")
def handle_start(address, args):
    print(f"Starting with arguments: {args}")


@server.add_handler("/stop")
def handle_stop(address, args):
    print(f"Stopping with arguments: {args}")


@server.add_handler("/playback")
def handle_playback(address, args):
    print(f"Playback with arguments: {args}")


def run_streamlit_app():
    subprocess.Popen(["streamlit", "run", "my_app.py"])


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
