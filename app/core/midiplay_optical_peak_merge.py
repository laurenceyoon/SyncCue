import numpy as np
import matplotlib.pyplot as plt
import cv2
from scipy.signal import medfilt
from scipy.signal import find_peaks
import mido
from mido import MetaMessage
import time

from .videocapture import VideoCaptureAsync


# 첫번째 코드에서 필요한 함수들 (calculate_optical_flow, send_midi)을 가져옵니다.
def calculate_optical_flow(prev_frame, curr_frame):
    prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    curr_gray = cv2.cvtColor(curr_frame, cv2.COLOR_BGR2GRAY)

    prev_points = cv2.goodFeaturesToTrack(
        prev_gray, maxCorners=100, qualityLevel=0.3, minDistance=7, blockSize=7
    )
    next_points, status, errors = cv2.calcOpticalFlowPyrLK(
        prev_gray, curr_gray, prev_points, None
    )

    # Calculate magnitude and angle of optical flow vectors
    flow_vectors = next_points - prev_points
    magnitude = np.sqrt(flow_vectors[..., 0] ** 2 + flow_vectors[..., 1] ** 2)
    angle = np.arctan2(flow_vectors[..., 1], flow_vectors[..., 0])

    # Calculate mean, velocity, and acceleration along the y-axis
    y_mean = np.mean(flow_vectors[..., 1])
    y_velocity = np.mean(magnitude * np.sin(angle))

    return y_mean, y_velocity


def send_midi(messages, port, seg_start, seg_end):
    for msg, delay in messages[seg_start:seg_end]:
        # print(msg, delay)
        if delay != 0.0:
            time.sleep(delay)

        port.send(msg)


# 두번째 코드에서 필요한 변수와 설정들을 가져옵니다.
feature_params = dict(maxCorners=1000, qualityLevel=0.01, minDistance=10, blockSize=50)
lk_params = dict(
    winSize=(15, 15),
    maxLevel=2,
    criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03),
)
color = np.random.randint(0, 255, (1000, 3))
isFirst = True
isSelect = False
threshold_max = 2
threshold_min = -2
n_frame = 0
frames = []

win_name = "test"
await_frames = 20

# MIDI 설정
port_index = 0
print(mido.get_output_names())
midi_file_path = "./test_beethoven.mid"  # 미디 파일 경로를 적절한 값으로 변경해주세요.


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


if __name__ == "__main__":
    print(
        f"MIDI Output Ports: {mido.get_output_names()}, selected: {mido.get_output_names()[port_index]}"
    )
    port = mido.open_output(mido.get_output_names()[port_index])

    cap = VideoCaptureAsync(0)

    print(f"FPS:{cap.fps}. Wait for webcam..., Press q to exit")
    time.sleep(2)
    cap.start_cache()
    start_time = cap.start_time
    print("Capture Started")
    capture_first = False

    n_frame = 0
    time_stamps = []
    y_mean_list = []
    cue = [None, None]
    while True:
        # capture first frame
        if not capture_first:
            frame, time_stamp = cap.capture()
            if frame is not None:
                print("First frame captured")
                capture_first = True
                last_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                p0 = cv2.goodFeaturesToTrack(last_frame, **feature_params)
                cap.empty_cache()
            continue

        # capture frame
        frame, time_stamp = cap.capture()
        if frame is not None:
            # update frame and calculate optical flow
            n_frame += 1
            current_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            p1, st, err = cv2.calcOpticalFlowPyrLK(
                last_frame, current_frame, p0, None, **lk_params
            )
            if p1 is not None:
                good_new = p1[st == 1]
                good_old = p0[st == 1]
            last_frame = current_frame.copy()
            p0 = p1
            time_stamps.append(time_stamp - start_time)
            y = -p1[:, 0, 1]
            y_mean = y.mean(axis=0)
            y_mean_list.append(y_mean)
            # framerate fluctuation is ignored
            y_vel = np.diff(y_mean_list)

            # wait for 20 frames
            if n_frame < await_frames and n_frame <= 5:
                continue

            y_vel_filt = medfilt(y_vel, 5)

            if np.any(y_vel_filt > threshold_max) and cue[0] is None:
                peaks, _ = find_peaks(y_vel_filt)
                if len(peaks) >= 1:
                    # cue detected
                    print(f"Cue Start detected: {peaks[0]}")
                    cue[0] = peaks[0]
                    continue

            if cue[0] is not None:
                min_start_index = cue[0]
                if np.any(y_vel_filt[min_start_index:] < threshold_min):
                    mins, _ = find_peaks(-y_vel_filt[min_start_index:])
                    if len(mins) >= 1:
                        # cue detected
                        cue[1] = mins[0] + min_start_index
                        print(f"Cue End detected: {cue[1]}")
                        break

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    if cue[0] is None or cue[1] is None:
        print("Cue not detected")
        exit()

    filter_delay = 2
    cue_start = time_stamps[cue[0] - filter_delay]
    cue_end = time_stamps[cue[1] - filter_delay]
    cue_est = cue_end + (cue_end - cue_start)
    cur_time = time.perf_counter() - start_time

    delay_adjust = 0.1
    time_left = cue_est - cur_time - delay_adjust

    if time_left > 0:
        print(f"Wait for {time_left:.2f} seconds")
        time.sleep(time_left)
        play_midi_file(midi_file_path, port)
    else:
        print("Cue already passed")
        play_midi_file(midi_file_path, port)
    cap.stop_cache()

    # print info for analysis
    print(
        f"cue_start: {cue_start:.2f}, cue_end: {cue_end:.2f}, cue_est: {cue_est:.2f}, cur_time: {cur_time:.2f}"
    )

    # plot
    time_stamps = np.array(time_stamps)
    plt.plot(time_stamps[1:], y_vel, "b")
    plt.plot(time_stamps[1:], y_vel_filt, "g")
    plt.plot(time_stamps[cue[0] - filter_delay + 1], y_vel_filt[cue[0]], "ro")
    plt.plot(time_stamps[cue[1] - filter_delay + 1], y_vel_filt[cue[1]], "ko")
    plt.axhline(cue_est, color="r", linestyle="--")
