import argparse
import subprocess
import time

from twisted.internet import reactor

from .core.cue_detection import cue_detection_start
from .core.midi_controller import midi_controller
from .database import Piece
from .osc_client import send_osc_end, send_osc_piece_info, send_osc_playback
from .osc_server import server


@server.add_handler("/start")
def handle_start(address, args=None):
    print(
        f"<== Received OSC message with {address}. Starting with arguments: {args, type(args)}"
    )
    piece_number = int(args)
    piece = Piece.objects(number=piece_number).first()
    send_osc_piece_info(piece.title, piece.composer)
    if piece.subpieces:
        subpieces = piece.subpieces
        for subpiece in subpieces:
            print(f"\nCue detection Start for Subpiece {subpiece.midi_path}")
            cue_detection_start(title=piece.title, midi_file_path=subpiece.midi_path)
            print(f"Subpiece {subpiece.midi_path} is done")
            time.sleep(subpiece.end_time_margin)
            print(f"end_time_margin {subpiece.end_time_margin} is done")
    else:
        cue_detection_start(title=piece.title, midi_file_path=piece.midi_path)


@server.add_handler("/stop")
def handle_stop(address, args=None):
    print(
        f"<== Received OSC message with {address}. Stopping with arguments: {args, type(args)}"
    )
    midi_controller.stop_midi()


@server.add_handler("/playback")
def handle_playback(address, args=None):
    print(
        f"<== Received OSC message with {address}. Playback with arguments: {args, type(args)}"
    )
    send_osc_playback(args)
    piece_info = args.split("-")
    piece_number = int(piece_info[0])
    piece = Piece.objects(number=piece_number).first()
    if len(piece_info) > 1 and piece.subpieces:  # subpiece 가 있는 경우, 예를 들어 args가 '1-2'
        subpiece_number = int(piece_info[1])
        subpiece = piece.subpieces[subpiece_number]
        midi_controller.play(midi_file_path=subpiece.midi_path)
    else:
        midi_controller.play(midi_file_path=piece.midi_path)
    send_osc_end()


def run_streamlit_app():
    subprocess.Popen(["streamlit", "run", "dashboard2/Home.py"])
    # Streamlit의 default local URL은 http://localhost:8501/이다.


if __name__ == "__main__":  # 직접 실행하게 되면 (% python -m app.main)
    parser = argparse.ArgumentParser()  # 인수 parser를 만든다.
    parser.add_argument(
        "--no-dashboard", action="store_true", help="Run server without dashboard"
    )  # parser.add_argument로 받아들일 인수를 추가해 나감; 옵션 인수는 -- 이렇게 이름 앞에 더해주자

    args = parser.parse_args()  # 커맨드라인의 인수를 분석

    if not args.no_dashboard:  # 만약 --no_dashboard가 인수로 존재하지 않았다면
        run_streamlit_app()  # Streamlit을 실행한다.

    reactor.listenUDP(8888, server)  # UDP; 포트9999를 listen
    reactor.run()  # 서버 구동
