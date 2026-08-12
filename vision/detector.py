import cv2
import numpy as np
import math
from ballObject import TennisBall
import random

def detectBall(frame):
    id = 0
    possibleBalls = []
    _, transformToBinary = cv2.threshold(frame, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    kernel = np.ones((3,3), np.uint8)
    # reduceNoiseFrame = cv2.morphologyEx(transformToBinary, cv2.MORPH_OPEN, kernel)
    # reduceNoiseFrame = cv2.morphologyEx(reduceNoiseFrame, cv2.MORPH_CLOSE, kernel)
    

    contours, _ = cv2.findContours(transformToBinary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        contourArea = cv2.contourArea(contour)
        if contourArea < 150 and contourArea > 2:
            perimeter = cv2.arcLength(contour, closed=True)

            if perimeter <= 0:
                continue

            circularity = (4*math.pi*contourArea) / (perimeter**2)
            (_, _), (width, height), _ = cv2.minAreaRect(contour)
            contourValues = cv2.moments(contour)

            if contourValues['m00'] == 0:
                continue
            cx = int(contourValues['m10'] / contourValues['m00'])
            cy = int(contourValues['m01'] / contourValues['m00'])
            radius = min(width, height)/2
            if radius != 0:
                if circularity > 0.8:
                    if 1.2 < (radius) < 4.5:
                        possibleBall = TennisBall(cx, cy, radius, contour, circularity, id)
                        possibleBalls.append(possibleBall)
                        id+=1
                    else:
                        continue  
                
                elif 0.3 < circularity < 0.40:
                    aspectRatio = max(width, height) / min(width, height)
                    if 1.5 < aspectRatio < 4:
                        if 1.2 < (radius) < 4.5:
                            possibleBall = TennisBall(cx, cy, radius, contour, circularity, id)
                            possibleBalls.append(possibleBall)
                            id+=1
                    else:
                        continue

                    
            else:
                continue

    maxCircularity = 0
    count = 0
    bestBall = None
    if len(possibleBalls) > 1:
        for i in range(1, len(possibleBalls)):
            circ = possibleBalls[i-1].getCircularity()
            prev_ballId = possibleBalls[i-1].getId()
            after_ballId = possibleBalls[i].getId()
            id_diff = abs(prev_ballId - after_ballId)
            if circ > maxCircularity:
                if id_diff < 2:
                    maxCircularity = circ
                    bestBall = possibleBalls[i-1]
    
    elif len(possibleBalls) == 1:
        bestBall = possibleBalls[0]
    return bestBall

def changeObj(ball):
    newBall = ball
    return newBall