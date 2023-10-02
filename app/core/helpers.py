from app.core.state_machine import StateMachine
from app.database import Piece
from app.osc_client import send_osc_piece_info, send_osc_playback

state_machine = None


def load_state_machine_for_performance(piece: Piece):
    global state_machine
    state_machine = StateMachine(piece)
    return state_machine


def cue_detection_start_for_piece(piece_id):
    piece_number = int(piece_id)
    piece = Piece.objects(number=piece_number).first()
    send_osc_piece_info(piece.title, piece.composer)
    state_machine = load_state_machine_for_performance(piece)
    state_machine.trigger_start()


def playback_start_for_piece(piece_num):
    global state_machine
    send_osc_playback(piece_num)
    piece_info = piece_num.split("-")
    piece_number = int(piece_info[0])
    piece = Piece.objects(number=piece_number).first()

    if state_machine is not None and state_machine.is_awake():
        state_machine.force_stop()
    state_machine = load_state_machine_for_performance(piece)

    if (
        len(piece_info) > 1 and piece.subpieces
    ):  # subpiece 가 있는 경우, 예를 들어 piece_num이 '1-2'
        subpiece_number = int(piece_info[1])
        state_machine.playback_start(subpiece_number=subpiece_number)
    else:
        state_machine.playback_start()


def all_stop_playing():
    if state_machine is not None:
        state_machine.force_stop()
