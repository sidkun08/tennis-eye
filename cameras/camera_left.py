import cv2
import numpy as np
from queue import Queue
import time

leftCamera = cv2.VideoCapture(0)
leftCamFrameQueue = Queue()

def start_left_camera():
    while True:
        ret, frame = leftCamera.read()
        
        if not ret:
            break
        
        timestamp = time.monotonic()
        cv2.imshow('Left Camera', frame)

        leftCamFrameQueue.put((timestamp, frame))

        if cv2.waitKey(1) & 0xFF == ord('l'):
            break

    leftCamera.release()
    cv2.destroyAllWindows()

