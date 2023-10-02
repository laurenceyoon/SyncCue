import mido

port_index = 0


class MidiController:
    def __init__(self):
        self.outport = None
        self.outport = mido.open_output()
        self.is_running = False

    def play(self, midi_file_path):
        mid = mido.MidiFile(midi_file_path)
        print(f"Play MIDI file: {midi_file_path}")
        self.is_running = True
        for msg in mid.play():
            if self.is_running:
                self.outport.send(msg)

    def stop_midi(self):
        self.outport.panic()
        self.is_running = False


midi_controller = MidiController()
