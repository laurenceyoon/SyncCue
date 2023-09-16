import mido
import time

from mido import MidiFile, MetaMessage

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

    def send(self, midi_file_path):
        midi = MidiFile(midi_file_path)
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


def send_midi(messages, port, seg_start, seg_end):
    for msg, delay in messages[seg_start:seg_end]:
        # print(msg, delay)
        if delay != 0.0:
            time.sleep(delay)

        port.send(msg)


def play_midi_file(midi_file_path, port):
    mid = mido.MidiFile(midi_file_path)
    tpb = mid.ticks_per_beat
    try:
        msgs = mid.tracks[1]
    except:
        msgs = mid.tracks[0]
    message_lists = []
    for msg in msgs:
        if isinstance(msg, MetaMessage):
            continue
        msg_time = mido.tick2second(msg.time, tpb, 500000)
        message_lists.append((msg, msg_time))

    send_midi(message_lists, port, 0, len(msgs))
