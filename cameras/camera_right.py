import cv2
import numpy as np
from queue import Queue
from threading import Thread
import time

rightCamera = cv2.VideoCapture(1)
rightCamFrameQueue = Queue()


while True:
    ret, frame = rightCamera.read()
    if not ret:
        break

    timestamp = time.monotonic()

    cv2.imshow('Right Camera', frame)

    rightCamFrameQueue.put((timestamp, frame))

    if cv2.waitKey(1) & 0xFF == ord('r'):
        break

rightCamera.release()
cv2.destroyAllWindows()