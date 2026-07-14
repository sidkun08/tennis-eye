import cv2
import numpy as np
import math

def detectBall(frame):
    _, transformToBinary = cv2.threshold(frame, 180, 255, cv2.THRESH_BINARY)
    kernel = np.ones((3,3), np.uint8)
    reduceNoiseFrame = cv2.morphologyEx(frame, cv2.MORPH_OPEN, kernel)
    reduceNoiseFrame = cv2.morphologyEx(reduceNoiseFrame, cv2.MORPH_CLOSE, kernel)
    contours, _ = cv2.findContours(reduceNoiseFrame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    areaOfTarget = cv2.contourArea(contours)

    if areaOfTarget < 200 or areaOfTarget > 5:
        circumference = cv2.arcLength(contours, True)
        circularity = (4*math.pi*areaOfTarget)/ (circumference**2)
        




    