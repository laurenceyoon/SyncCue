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
#===== Client로써 Unity에게 신호 전송 =====
import argparse
import random
import time
import sys
from pythonosc import udp_client
#=====================

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

file_num = 0 # midi_files_list 속 원소들의 index; 0:test_beethoven ~ 6:fermatacue_ai_3
midi_files_list = ["test_beethoven",
                   "startcue_ai_original",
                   "startcue_ai_revised",
                   "fermatacue_ai_1",
                   "fermatacue_ai_2",
                   "fermatacue_ai_3"]
midi_file_path = "./resources/midi/"+midi_files_list[file_num]+".mid"

port_index = 0
threshold_max = 1
threshold_min = -1
delay_adjust = 0.25

#==============Client로써 전달할 정보들을 불러오기 위해 전역변수와 함수를 정의============
time_stamp = np.ndarray([]); y_vel = np.ndarray([]); y_vel_filt = np.ndarray([]); cue = [None, None]

def write_cue_start():
    with open(os.getcwd()+'/'+midi_files_list[file_num]+"/cue_info.csv", 'w', newline='') as f:
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
    global y_vel
    global time_stamp
    global y_vel_filt
    global cue
    #======OSC 통신========
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", default="127.0.0.1", help="The ip of the OSC server")
    parser.add_argument("--port", type=int, default=5005, help="The port the OSC server is listening on")
    args = parser.parse_args()
    client = udp_client.SimpleUDPClient(args.ip, args.port)
    #=====================
    
    print(f"MIDI Output Ports: {mido.get_output_names()}, selected: {mido.get_output_names()[port_index]}")
    port = mido.open_output(mido.get_output_names()[port_index])

    cap = VideoCaptureAsync(0)
    cap.fps = 30 # set fps
    cap.start_cache() # 비디오 캡처 시작
    start_time = cap.start_time # 시작 시간 기록
    # Initialize VideoWriter
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # or use 'XVID'
    out = cv2.VideoWriter('output_video_0831.mp4', fourcc, 30.0, (640, 480))  # Assuming frame size is 640x480, and FPS is 30
    initial_rect = None  # New variable to hold the detected face area

    print(f"FPS:{cap.fps}. Wait for webcam..., Press q to exit")
    time.sleep(2)
    cap.start_cache()
    start_time = cap.start_time
    print("Capture Started")
    client.send_message("/start", 1) # OSC 통신 (1) - Capture Start
    capture_first = False # 6프레임부터 True로 변경
    
    n_frame = 0
    time_stamps = []
    y_mean_list = []
    
    # with문은 자원을 획득, 사용, 반납할 때 사용된다. 객체의 라이프사이클을 설계; with EXPRESSION [as VARIABLE]: BLOCK
    with mp_face_detection.FaceDetection(model_selection=0, min_detection_confidence=0.5) as face_detection:
        while True:
            ### Capture the first frame
            if not capture_first:
                frame, time_stamp = cap.capture()
                if frame is not None:
                    height, width, channels = frame.shape  # 프레임의 높이, 너비, 채널 수를 얻습니다.
                    # 5프레임 동안은 얼굴을 인식하지 않습니다. (while 루프 다음 스테이지로 스킵)
                    if n_frame < 5: n_frame += 1; continue
                    
                    # 6프레임~results.detection==True일 때까지: Perform face detection here
                    rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    results = face_detection.process(rgb_image)
                    if results.detections:
                        assert (len(results.detections) == 1), 'More than one face detected' # 사람이 한 명이어야 함 (강제)
                        for detection in results.detections:
                            bboxC = detection.location_data.relative_bounding_box
                            ih, iw, _ = frame.shape
                            x, y, w, h = int(bboxC.xmin * iw), int(bboxC.ymin * ih), int(bboxC.width * iw), int(bboxC.height * ih)
                            print(f'Face detected at {x}, {y}, {w}, {h}')
                            initial_rect = (x, y, w, h)  # Save the detected face area
                        print('** First frame captured **')
                        capture_first = True
                        last_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                        # if initial_rect:
                        x, y, w, h = initial_rect
                        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

                        p0 = cv2.goodFeaturesToTrack(last_frame, **feature_params)
                        # remove features outside the face area
                        p0 = p0[(p0[:, 0, 0] > x) & (p0[:, 0, 0] < x+w) & (p0[:, 0, 1] > y) & (p0[:, 0, 1] < y+h)]

                    cap.empty_cache()
                    # # Save frame to video
                    out.write(frame)
                continue
            
            ### After capture the first frame
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
                    for i, (new, old) in enumerate(zip(good_new, good_old)):
                            a, b = new.ravel()
                            c, d = old.ravel()
                            cv2.line(frame, (int(a), int(b)), (int(c), int(d)), (0, 255, 0), 2)
                            cv2.circle(frame, (int(a), int(b)), 5, (0, 0, 255), -1)

                out.write(frame)
                    
                last_frame = current_frame.copy()
                p0 = p1
                time_stamps.append(time_stamp - start_time)
                y = -p1[:, 0, 1]
                y_mean = y.mean(axis=0)
                y_mean_list.append(y_mean)
                # framerate fluctuation is ignored
                y_vel = np.diff(y_mean_list)
                # np.diff에 대한 설명: 리스트 내부에 인접한 숫자 아이템 간의 오차를 담는다 (기존 n개 -> n-1개로 아이템 개수 줄어듦)
                # x = np.array([1, 2, 4, 7, 0])
                # np.diff(x)
                # array([ 1,  2,  3, -7])

                # wait for 20 frames
                if n_frame < await_frames and n_frame <= 5:
                    continue

                y_vel_filt = medfilt(y_vel, 5)

                if cue[0] == None:
                    peaks, _ = find_peaks(y_vel_filt, height=threshold_max)
                    if len(peaks) >= 1:
                        # cue detected
                        print(f"Cue Start detected: {peaks[0]}")
                        cue[0] = peaks[0] # Cue Start (Bottom Cue 탐지)
                        write_cue_start()
                        continue
                else: # if cue[0] != None
                    min_start_index = cue[0]
                    mins, _ = find_peaks(
                        -y_vel_filt[min_start_index:], height=threshold_min
                    )
                    if len(mins) >= 1:
                        # cue detected
                        cue[1] = mins[0] + min_start_index
                        print(f"Cue End detected: {cue[1]}")
                        if cue[1] and cue[0] != None:
                            client.send_message("/detect", str(cue[1]-cue[0])) # OSC 통신 (2) - Detect
                        write_cue_end()
                        break

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        if cue[0] == None or cue[1] == None:
            print("Cue not detected")
            exit()

    # <end> of with문
    
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

# First Frame Capture
# Estimate Note Onset (Min Peak)
# Note Onset

# First Frame 시그널 (bool)
# Min Peak + 차오르는 시간 (bool + float)
# MIDI Off (0.몇초 전) -> 지윤누나