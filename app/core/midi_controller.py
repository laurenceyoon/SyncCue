import mido
import time

from mido import MidiFile, MetaMessage

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

    def send_midi_msg(self, messages, seg_start, seg_end):
        for msg, delay in messages[seg_start:seg_end]:
            # print(msg, delay)
            if delay != 0.0:
                time.sleep(delay)

            self.outport.send(msg)

    def play(self, midi_file_path):
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

        self.send_midi_msg(message_lists, 0, len(msgs))

    def stop_midi(self):
        self.outport.panic()


midi_controller = MidiController()
