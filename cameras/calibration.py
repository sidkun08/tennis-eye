import cv2
from camera_left import leftCamFrameQueue
from camera_right import rightCamFrameQueue
from config import FRAMES_PER_SECTION
from queue import Queue

fixedleftCamFrameQue = Queue()
fixedrightCamFrameQue = Queue()

num = 0
while num < FRAMES_PER_SECTION:
    timestampL, frameLeft = leftCamFrameQueue.get()
    cv2.calibrateCamera(frameLeft)
    timestampR, frameRight = rightCamFrameQueue.get() 
    num+=1

    
    