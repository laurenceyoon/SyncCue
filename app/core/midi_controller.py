import mido

from mido import MidiFile

# from ..config import MIDI_PORT_NAME


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

    def send(self, midi: MidiFile):
        if self.outport is None:
            self.outport = mido.open_output()
        self.is_running = True

        # start playing
        for msg in midi.play():
            if self.is_running:
                self.outport.send(msg)
            else:
                print("Stop sending MIDI messages!")
                return
        # end of playing
        self.is_running = False

    def panic(self):
        self.is_running = False
        self.outport.panic()


midi_port = MidiController()
