import mido
import time
import threading

from app.config import CONNECTION_INTERVAL


class MidiController:
    def __init__(self, connection_interval: int):
        self.interval = connection_interval
        self.outport = None
        self.is_running = False
        self.connect_to_midi_port()

    def connect_to_midi_port(self):
        thread = threading.Thread(target=self._connect_to_midi_port)
        thread.start()

    def _connect_to_midi_port(self):
        while True:
            try:
                if self.outport is None:
                    self.outport = mido.open_output(autoreset=True)
                    print(f"💡 MIDI PORT CONNECTED 🔌 {self.outport}")
                    break
            except Exception as e:
                print(
                    f"Failed to connect to MIDI port. Error: {e}. Retrying in {self.interval} seconds..."
                )
                time.sleep(self.interval)

    def play(self, midi_file_path):
        mid = mido.MidiFile(midi_file_path)
        print(f"Play MIDI file: {midi_file_path}")
        self.is_running = True
        for msg in mid.play():
            if self.is_running:
                self.outport.send(msg)
            else:
                print("Stop sending MIDI messages!")
                return

    def stop_midi(self):
        self.outport.panic()
        self.is_running = False


midi_controller = MidiController(connection_interval=CONNECTION_INTERVAL)
