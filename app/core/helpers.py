from app.core.cue_detection import cue_detection_start
from app.osc_client import send_osc_end, send_osc_piece_info, send_osc_playback
from .state_machine import StateMachine
from ..database import Piece
import asyncio
from .midi_controller import midi_controller

state_machine = None


def load_state_machine_for_performance(piece: Piece):
    global state_machine
    state_machine = StateMachine(piece)
    return state_machine


def trigger_intro_performance():
    state_machine.trigger_intro()


def trigger_start_cue_detection():
    state_machine.trigger_start()


async def run_in_background(func, *args, **kwargs):
    return await asyncio.to_thread(func, *args, **kwargs)


async def cue_detection_start_for_piece(piece_id):
    global state_machine
    piece_number = int(piece_id)
    piece = Piece.objects(number=piece_number).first()
    send_osc_piece_info(piece.title, piece.composer)
    state_machine = load_state_machine_for_performance(piece)
    if piece.subpieces:
        subpieces = piece.subpieces
        for subpiece in subpieces:
            print(f"\nCue detection Start for Subpiece {subpiece.midi_path}")
            await run_in_background(
                cue_detection_start,
                title=piece.title,
                midi_file_path=subpiece.midi_path,
            )
            print(f"Subpiece {subpiece.midi_path} is done")
            print(f"end_time_margin {subpiece.end_time_margin} is done")
    else:
        await run_in_background(
            cue_detection_start, title=piece.title, midi_file_path=piece.midi_path
        )


def all_stop_playing():
    midi_controller.stop_midi()
    # if state_machine is not None:
    #     state_machine.trigger_stop()


def playback_for_piece(piece_num):
    send_osc_playback(piece_num)
    piece_info = piece_num.split("-")
    piece_number = int(piece_info[0])
    piece = Piece.objects(number=piece_number).first()
    if len(piece_info) > 1 and piece.subpieces:  # subpiece 가 있는 경우, 예를 들어 args가 '1-2'
        subpiece_number = int(piece_info[1])
        subpiece = piece.subpieces[subpiece_number]
        midi_controller.play(midi_file_path=subpiece.midi_path)
    else:
        midi_controller.play(midi_file_path=piece.midi_path)
    send_osc_end()
