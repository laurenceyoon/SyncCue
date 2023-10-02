from transitions import Machine
from ..database import Piece, SubPiece


class StateMachine:
    states = [
        "asleep",
        "intro",
        "start",
        "detected",
        "playback",
        "stop",
        "outro",
    ]

    def __init__(self, piece: Piece) -> None:
        self.piece = piece
        self.subpieces = []  # subpieces 일 수도, 하나의 piece 일 수도
        self.current_piece = None
        self.machine = Machine(model=self, states=StateMachine.states, initial="asleep")
        self.machine.add_transition(
            trigger="trigger_intro",
            source="asleep",
            dest="intro",
            after="transit_to_intro_state",
        )
        self.machine.add_transition(
            trigger="trigger_start",
            source=["asleep", "intro"],
            dest="start",
            after="transit_to_cue_detection_start",
        )
        self.machine.add_transition(
            trigger="trigger_playback",
            source=["asleep", "start"],
            dest="playback",
            after="transit_to_playback",
        )
        self.machine.add_transition(
            trigger="trigger_stop",
            source=[
                "asleep",
                "intro",
                "start",
                "detected",
                "playback",
                "stop",
                "outro",
            ],
            dest="stop",
            after="transit_to_stop",
        )
