import time

import mido
from mido import MetaMessage

port_index = 0
# port = mido.open_output()


class MidiController:
    def __init__(self):
        self.outport = None
        self.is_running = False
        try:
            outport = mido.open_output()
        except OSError:
            pass
        else:
            self.outport = outport

    def play(self, midi_file_path):
        mid = mido.MidiFile(midi_file_path)
        for msg in mid.play():
            self.outport.send(msg)

    def stop_midi(self):
        self.outport.panic()


midi_controller = MidiController()
