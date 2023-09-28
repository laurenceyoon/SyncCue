import time

import mido
from mido import MetaMessage

port_index = 0


class MidiController:
    def __init__(self):
        self.outport = None
        self.outport = mido.open_output()

    def play(self, midi_file_path):
        mid = mido.MidiFile(midi_file_path)
        print(f"Play MIDI file: {midi_file_path}")
        for msg in mid.play():
            self.outport.send(msg)
        # self.stop_midi()

    def stop_midi(self):
        self.outport.panic()


midi_controller = MidiController()
