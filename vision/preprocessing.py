from cameras.camera_left import leftCamFrameQueue
from cameras.camera_right import rightCamFrameQueue
from queue import Queue
import cv2

newLeftFrameQueue = Queue()
newRightFrameQueue = Queue()

while True:
    leftFrame = leftCamFrameQueue.get()[1]
    rightFrame = rightCamFrameQueue.get()[1]

    
