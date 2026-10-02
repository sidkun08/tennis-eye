import cv2
import numpy as np

def getCalibratedMatrix(frame):
    grayscale = cv2.colorChange(frame, cv2.COLOR_BGR2GRAY)
    found, corners = cv2.findChessboardCorners(grayscale, (9, 6))

    if found:
        winzone = (11, 11)
        zeroZone = (-1, -1)
        criteria = (cv2.TermCriteria_EPS + cv2.TermCriteria_MAX_ITER, 30, 0.001)
        corners = cv2.cornerSubPix(grayscale, corners, winzone, zeroZone, criteria)
        
        