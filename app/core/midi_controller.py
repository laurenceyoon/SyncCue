import mido
import time

from mido import MidiFile, MetaMessage

# from ..config import MIDI_PORT_NAME
port_index = 0
port = mido.open_output()


def send_midi(messages, seg_start, seg_end):
    for msg, delay in messages[seg_start:seg_end]:
        # print(msg, delay)
        if delay != 0.0:
            time.sleep(delay)

        port.send(msg)


def play_midi_file(midi_file_path):
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

    send_midi(message_lists, 0, len(msgs))
