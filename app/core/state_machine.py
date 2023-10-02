from transitions import Machine
from app.database import Piece
from collections import deque
from app.osc_client import send_osc_end
from app.core.cue_detector import cue_detector
from app.core.midi_controller import midi_controller


class StateMachine:
    states = ["asleep", "cue_detect", "playback"]

    def __init__(self, piece: Piece) -> None:
        self.piece = piece
        if piece.subpieces:
            self.schedules = deque(piece.subpieces)
        else:
            self.schedules = deque([piece])  # schedule은 subpieces 일 수도, 하나의 piece 일 수도
        self.current_schedule = self.schedules.popleft()
        self.machine = Machine(model=self, states=StateMachine.states, initial="asleep")
        self.machine.add_transition(
            trigger="trigger_start",
            source=["asleep", "cue_detect"],
            dest="cue_detect",
            after="transit_to_cue_detect",
        )
        self.machine.add_transition(
            trigger="trigger_playback",
            source=["asleep", "cue_detect"],
            dest="playback",
            after="transit_to_playback",
        )
        self.machine.add_transition(
            trigger="trigger_stop",
            source=["asleep", "cue_detect", "playback"],
            dest="asleep",
            before="broadcast_stop",
        )
        self.machine.add_transition(
            trigger="force_stop",
            source=["asleep", "cue_detect", "playback"],
            dest="asleep",
            before="broadcast_and_panic_stop",
        )
        self.machine.add_transition(
            trigger="trigger_playback",
            source="asleep",
            dest="playback",
            before="broadcast_stop",
        )

    def is_next_schedule_exist(self):
        return len(self.schedules) > 0

    def transit_to_cue_detect(self):
        print(
            f"\nCue detect Start r current schedule {self.current_schedule.midi_path}"
        )
        cue_detector.start(
            title=self.piece.title, midi_file_path=self.current_schedule.midi_path
        )
        print(f"Current schedule {self.current_schedule.midi_path} is done")
        self.broadcast_stop()
        self.move_to_next()

    def move_to_next(self):
        if self.is_next_schedule_exist():
            self.current_schedule = self.schedules.popleft()
            self.trigger_start()
        else:
            self.trigger_stop()

    def playback_start(self, subpiece_number=None):
        cue_detector.stop_detecting()
        if subpiece_number:
            subpiece = self.piece.subpieces[subpiece_number]
            midi_controller.play(midi_file_path=subpiece.midi_path)
        else:
            midi_controller.play(midi_file_path=self.current_schedule.midi_path)
        send_osc_end()

    def broadcast_stop(self):
        print("** 🛑 Stop all playing **")
        send_osc_end()

    def broadcast_and_panic_stop(self):
        print("** 🛑🛑 [FORCE] Stop all playing (panic) 🛑🛑 **")
        send_osc_end()
        midi_controller.stop_midi()
