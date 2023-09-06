import numpy as np
import matplotlib.pyplot as plt
import cv2
from scipy.signal import medfilt
from scipy.signal import find_peaks
import mido
from mido import MetaMessage
import time
from .videocapture import VideoCaptureAsync
from .midiplay_optical_peak_merge import port_index, await_frames, play_midi_file
import csv # list를 csv 형태로 저장
import os

#=======Face Detection 추가 (0903)==============================================
import mediapipe as mp
mp_face_detection = mp.solutions.face_detection
face_detection = mp_face_detection.FaceDetection(min_detection_confidence=0.1)
#==============================================================================

# def process_video_capture(midi_file_path, port_index) in cue_performance.ipynb
feature_params = dict(maxCorners=1000, qualityLevel=0.01, minDistance=10, blockSize=50)
lk_params = dict(
    winSize=(15, 15),
    maxLevel=2,
    criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03),
)

midi_file_path = "./resources/midi/test_beethoven.mid"
# "./resources/midi/startcue_ai_original.mid"
# "./resources/midi/startcue_ai_revised.mid"
# "./resources/midi/fermatacue_ai_1.mid"
# "./resources/midi/fermatacue_ai_2.mid"
# "./resources/midi/fermatacue_ai_3.mid"

port_index = 0
threshold_max = 1
threshold_min = -1
delay_adjust = 0.25

#==============Client로써 전달할 정보들을 불러오기 위해 전역변수와 함수를 정의============
time_stamp = None; y_vel = None; y_vel_filt = None; cue = [None, None]
    
def write_cue_start():
    with open(os.getcwd()+"/cue_info.csv", 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["type", f"time_stamp ({type(time_stamp)})", f"y_vel {y_vel.shape, type(y_vel)}", f"y_vel_filt {y_vel_filt.shape, type(y_vel_filt)}", f"cue ({type(cue)})"])
        writer.writerow(["start", time_stamp, y_vel, y_vel_filt, cue])

def write_cue_end():
    with open(os.getcwd()+"/cue_info.csv", 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["end", time_stamp,y_vel, y_vel_filt, cue])
        

def get_info(): # Client로써 전달할 정보들을 불러오는 메소드 (튜플 형태)
    return time_stamp, y_vel, y_vel_filt, cue
#===========================================================================

def cue_detection_start():
    print(
        f"MIDI Output Ports: {mido.get_output_names()}, selected: {mido.get_output_names()[port_index]}"
    )
    port = mido.open_output(mido.get_output_names()[port_index])

    cap = VideoCaptureAsync(0)
    cap.fps = 120

    print(f"FPS:{cap.fps}. Wait for webcam..., Press q to exit")
    time.sleep(2)
    cap.start_cache()
    start_time = cap.start_time
    print("Capture Started")
    capture_first = False

    #==== 전역변수 활용 ====
    global time_stamp
    global y_vel
    global y_vel_filt
    global cue
    #==== 전역변수 활용 ====
    
    n_frame = 0
    time_stamps = []
    y_mean_list = []
    
    while True:
        print(f"cue:{cue}")
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

            if cue[0] is None:
                peaks, _ = find_peaks(y_vel_filt, height=threshold_max)
                if len(peaks) >= 1:
                    # cue detected
                    print(f"Cue Start detected: {peaks[0]}")
                    cue[0] = peaks[0] # Cue Start (Bottom Cue 탐지)
                    write_cue_start()
                    continue

            if cue[0] is not None:
                min_start_index = cue[0]
                mins, _ = find_peaks(
                    -y_vel_filt[min_start_index:], height=threshold_min
                )
                if len(mins) >= 1:
                    # cue detected
                    cue[1] = mins[0] + min_start_index
                    print(f"Cue End detected: {cue[1]}")
                    write_cue_end()
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

    time_left = cue_est - cur_time - delay_adjust

    if time_left > 0:
        print(f"Wait for {time_left:.2f} seconds")
        time.sleep(time_left)
        play_midi_file(midi_file_path, port)
    else:
        print("Cue already passed")
        play_midi_file(midi_file_path, port)
    cap.stop_cache()
