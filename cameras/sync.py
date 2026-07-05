import cv2
from camera_left import leftCamFrameQueue
from camera_right import rightCamFrameQueue
from queue import Queue
from config import TIME_DIFF

syncedFrameQueue = Queue()

while True:

    leftTimeStamp, leftCamFrame = leftCamFrameQueue.get()
    rightTimeStamp, rightCamFrame = rightCamFrameQueue.get()

    time_diff = abs(leftTimeStamp-rightTimeStamp)

    if time_diff <= TIME_DIFF:
        avgTime = (leftTimeStamp + rightTimeStamp)/2
        syncedFrameQueue.put((avgTime, leftCamFrame, rightCamFrame))

    else:
        
        if leftTimeStamp > rightTimeStamp:
            leftCamFrameQueue.get()
            syncedFrameQueue.put((rightTimeStamp, rightCamFrame))
        else:
            rightCamFrameQueue.get()
            syncedFrameQueue.put((leftTimeStamp, leftCamFrame))
    


