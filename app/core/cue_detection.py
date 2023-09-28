import csv
import datetime
import os
import time

import cv2
import mediapipe as mp
import numpy as np
from scipy.signal import find_peaks, medfilt

from ..osc_client import send_osc_detect, send_osc_end, send_osc_start
from .midi_controller import midi_controller
from .videocapture import VideoCaptureAsync

feature_params = dict(maxCorners=1000, qualityLevel=0.01, minDistance=10, blockSize=50)
lk_params = dict(
    winSize=(15, 15),
    maxLevel=2,
    criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03),
)

threshold_max = 1
threshold_min = -1
delay_adjust = 0
await_frames = 20
system_delay = 0.25

# ==============Client로써 전달할 정보들을 불러오기 위해 전역변수와 함수를 정의============
time_stamp = np.ndarray([])
y_vel = np.ndarray([])
y_vel_filt = np.ndarray([])
cue = [None, None]


def write_cue_start(title):
    with open(os.getcwd() + "/cue_info.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "type",
                f"time_stamp ({type(time_stamp)})",
                f"y_vel {y_vel.shape, type(y_vel)}",
                f"y_vel_filt {y_vel_filt.shape, type(y_vel_filt)}",
                f"cue ({type(cue)})",
            ]
        )
        writer.writerow(["start", time_stamp, y_vel, y_vel_filt, cue])


def write_cue_end(title):
    with open(os.getcwd() + "/cue_info.csv", "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["end", time_stamp, y_vel, y_vel_filt, cue])


def get_info():  # Client로써 전달할 정보들을 불러오는 메소드 (튜플 형태)
    return time_stamp, y_vel, y_vel_filt, cue


# ===========================================================================


def cue_detection_start(title, midi_file_path):
    global y_vel
    global time_stamp
    global y_vel_filt
    global cue
    # =====================
    time_stamp = np.ndarray([])
    y_vel = np.ndarray([])
    y_vel_filt = np.ndarray([])
    cue = [None, None]

    cap = VideoCaptureAsync(0)
    cap.fps = 30  # set fps
    cap.start_cache()  # 비디오 캡처 시작
    start_time = cap.start_time  # 시작 시간 기록
    # Initialize VideoWriter
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")  # or use 'XVID'
    out = cv2.VideoWriter(
        f"output_video_{datetime.datetime.now().isoformat()}.mp4",
        fourcc,
        30.0,
        (640, 480),
    )  # Assuming frame size is 640x480, and FPS is 30
    initial_rect = None  # New variable to hold the detected face area

    print(f"FPS:{cap.fps}. Wait for webcam..., Press q to exit")
    time.sleep(2)
    cap.start_cache()
    start_time = cap.start_time
    print("Capture Started")
    # capture start osc 보내주자!
    capture_first = False  # 6프레임부터 True로 변경

    n_frame = 0
    time_stamps = []
    y_mean_list = []

    # with문은 자원을 획득, 사용, 반납할 때 사용된다. 객체의 라이프사이클을 설계; with EXPRESSION [as VARIABLE]: BLOCK
    mp_face_detection = mp.solutions.face_detection
    with mp_face_detection.FaceDetection(
        model_selection=0, min_detection_confidence=0.5
    ) as face_detection:
        while True:
            ### Capture the first frame
            if not capture_first:
                frame, time_stamp = cap.capture()
                if frame is not None:
                    height, width, channels = frame.shape  # 프레임의 높이, 너비, 채널 수를 얻습니다.
                    # 5프레임 동안은 얼굴을 인식하지 않습니다. (while 루프 다음 스테이지로 스킵)
                    if n_frame < 5:
                        n_frame += 1
                        continue

                    # 6프레임~results.detection==True일 때까지: Perform face detection here
                    rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    results = face_detection.process(rgb_image)
                    if results.detections:
                        assert (
                            len(results.detections) == 1
                        ), "More than one face detected"  # 사람이 한 명이어야 함 (강제)
                        for detection in results.detections:
                            bboxC = detection.location_data.relative_bounding_box
                            ih, iw, _ = frame.shape
                            x, y, w, h = (
                                int(bboxC.xmin * iw),
                                int(bboxC.ymin * ih),
                                int(bboxC.width * iw),
                                int(bboxC.height * ih),
                            )
                            print(f"Face detected at {x}, {y}, {w}, {h}")
                            initial_rect = (x, y, w, h)  # Save the detected face area
                        print("** First frame captured **")
                        send_osc_start()  # OSC 통신 (1) - Capture Start
                        capture_first = True
                        last_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                        # if initial_rect:
                        x, y, w, h = initial_rect
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                        p0 = cv2.goodFeaturesToTrack(last_frame, **feature_params)
                        # remove features outside the face area
                        p0 = p0[
                            (p0[:, 0, 0] > x)
                            & (p0[:, 0, 0] < x + w)
                            & (p0[:, 0, 1] > y)
                            & (p0[:, 0, 1] < y + h)
                        ]

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
                        cv2.line(
                            frame, (int(a), int(b)), (int(c), int(d)), (0, 255, 0), 2
                        )
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

                # wait for 20 frames
                if n_frame < await_frames and n_frame <= 5:
                    continue

                y_vel_filt = medfilt(y_vel, 5)

                if cue[0] is None:
                    peaks, _ = find_peaks(y_vel_filt, height=threshold_max)
                    if len(peaks) >= 1:
                        # start cue detected
                        print(f"Cue Start detected: {peaks[0]}")
                        cue[0] = peaks[0]  # Cue Start (Bottom Cue 탐지)
                        write_cue_start(title)
                        continue
                else:
                    min_start_index = cue[0]
                    mins, _ = find_peaks(
                        -y_vel_filt[min_start_index:], height=threshold_min
                    )
                    if len(mins) >= 1:
                        # end cue detected
                        cue[1] = mins[0] + min_start_index
                        time_delay = time_stamps[-1] - time_stamps[cue[1]]
                        print(f"Cue End detected: {cue[1]}")
                        print(f"time_delay: {time_delay}")
                        if cue[1] and cue[0]:
                            send_osc_detect(
                                ((cue[1] - cue[0]) * 1 / cap.fps)
                                - time_delay
                                - system_delay
                            )  # OSC 통신 (2) - Detect
                        write_cue_end(title)
                        break

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        if cue[0] is None or cue[1] is None:
            print("Cue not detected")
            exit()
    cap.stop_cache()
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
        midi_controller.play(midi_file_path)
    else:
        print("Cue already passed")
        midi_controller.play(midi_file_path)
    send_osc_end()  # OSC 통신 (3) - End of MIDI

    # cap.cap.release()


# First Frame Capture
# Estimate Note Onset (Min Peak)
# Note Onset

# First Frame 시그널 (bool)
# Min Peak + 차오르는 시간 (bool + float)
# MIDI Off (0.몇초 전) -> 지윤누나
