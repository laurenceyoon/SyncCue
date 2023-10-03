import threading
import time

import cv2

# Copy from https://stackoverflow.com/questions/60501795/asynchronous-list-of-videos-to-be-stream-using-opencv-in-python


class VideoCaptureAsync:
    def __init__(self, src=0, width=640, height=480):
        self.src = src
        self.cap = cv2.VideoCapture(self.src)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.start_time = time.perf_counter()
        self.started = False

    def start_cache(self):
        self.started = True
        self.cache = []
        self.cache_lock = threading.Lock()
        self.cache_thread = threading.Thread(target=self.cache_update, args=())
        self.cache_thread.start()
        return self

    def cache_update(self):
        while self.started:
            grabbed, frame = self.cap.read()
            with self.cache_lock:
                if grabbed:
                    time_stamp = time.perf_counter()
                    self.cache.append((frame, time_stamp))

    def empty_cache(self):
        with self.cache_lock:
            self.cache = []

    def stop_cache(self):
        self.started = False
        self.cache_thread.join()

    def capture(self):
        with self.cache_lock:
            if len(self.cache) > 0:
                frame, time_stamp = self.cache.pop(0)
                return frame, time_stamp
            else:
                return None, None

    def __exit__(self, exec_type, exc_value, traceback):
        self.cap.release()
