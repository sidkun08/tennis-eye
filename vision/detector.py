import cv2
import numpy as np
import math
from config import BALL_RADIUS_LOWER, BALL_RADIUS_UPPER
from detectorFunctions import checkLargestSize

def detectBall(frame):
    ballDictionary = {}
    _, transformToBinary = cv2.threshold(frame, 180, 255, cv2.THRESH_BINARY)
    kernel = np.ones((3,3), np.uint8)
    reduceNoiseFrame = cv2.morphologyEx(frame, cv2.MORPH_OPEN, kernel)
    reduceNoiseFrame = cv2.morphologyEx(reduceNoiseFrame, cv2.MORPH_CLOSE, kernel)
    contours, _ = cv2.findContours(reduceNoiseFrame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    areaOfTarget = cv2.contourArea(contours)

    if areaOfTarget < 200 or areaOfTarget > 5:
        circumference = cv2.arcLength(contours, True)
        circularity = (4*math.pi*areaOfTarget)/ (circumference**2)
        (x,y), rad = cv2.minEnclosingCircle(contours)
        if abs(1-circularity) < 0.1:
            if (rad < BALL_RADIUS_UPPER) and (rad > BALL_RADIUS_LOWER):
                ballDictionary["center_x"] = x
                ballDictionary["center_y"] = y
                ballDictionary["radius"] = rad
    
    if len(ballDictionary) > 1:
        value = checkLargestSize(ballDictionary)
        x = ballDictionary.get(value)[0]
        y = ballDictionary.get(value)[1]
        rad = ballDictionary.get(value)[2]
        return (x, y), rad
    else:
        return (x, y), rad
        