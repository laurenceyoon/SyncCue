### OSC UDP Client (For Communication with Unity)

#import argparse # Python의 실행시에 커맨드 라인 인수를 다룰 때, ArgumentParser(argparse)를 사용하면 편리하다.
#from .osc_client import OSCUDPClient
from .core.cue_detection import get_info
import time

# client = OSCUDPClient() # self.handlers = {} 빈 딕셔너리

"""
- .core.cue_detection에서 framewise 통신에 필요한 것
  - timestamp
  - y_vel
  - y_vel_filt (medfilter 적용된 값)
  
  큐 디텍션을 위한 
  
  cue[0] = 
"""

try: # Down
    while True:
        time_stamp, y_vel, y_vel_filt, cue = get_info()
        print(f"cue: {cue}")
        if cue[0] is not None:
            print("Bottom Cue")
            break
        #time.sleep(1) # Time Sleep for 1 second
except KeyboardInterrupt: pass

try: # Up
    while True: # 1초마다 받아오고 있음
        print("Second Phase")
        time_stamp, y_vel, y_vel_filt, cue = get_info()
        print(f"{time_stamp}, {y_vel}, {y_vel_filt}, {cue}")
        if cue[1] is not None:
            print("Top Cue")
            break
except KeyboardInterrupt: pass
print("Done")