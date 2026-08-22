import cv2
import numpy as np
import math
from ballObject import TennisBall
import random
from preprocessing import is_moving

def detectBall(frame):
    possibleBalls = []
    _, transformToBinary = cv2.threshold(frame, 180, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    kernel = np.ones((3,3), np.uint8)
    reduceNoiseFrame = cv2.morphologyEx(transformToBinary, cv2.MORPH_OPEN, kernel)
    reduceNoiseFrame = cv2.morphologyEx(reduceNoiseFrame, cv2.MORPH_CLOSE, kernel)
    

    contours, _ = cv2.findContours(transformToBinary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        contourArea = cv2.contourArea(contour)
        if contourArea < 170 and contourArea > 20:
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
                    aspect_ratio = max(width, height) / (radius)
                    if 1.5 < aspect_ratio < 4:
                        if 0.8< (radius) < 4.5:
                            possibleBall = TennisBall(cx, cy, radius, contour, circularity)
                            possibleBalls.append(possibleBall)
                        else:
                            continue  
                '''
                elif 0.35 < circularity < 0.4:
                    aspectRatio = max(width, height) / min(width, height)
                    if 1.5 < aspectRatio < 4:
                        if 2 < (radius) < 4:
                            possibleBall = TennisBall(cx, cy, radius, contour, circularity, id)
                            possibleBalls.append(possibleBall)
                            id+=1
                    else:
                        continue

                 '''   
            else:
                continue

    maxCircularity = 0
    count = 0
    bestBall = None


    
    if len(possibleBalls) > 2:
        for i in range(1, len(possibleBalls)):
            circ = possibleBalls[i-1].getCircularity()
            if circ > maxCircularity:
                
                maxCircularity = circ
                bestBall = possibleBalls[i-1]
    
    if len(possibleBalls) == 1:
        bestBall = possibleBalls[0]
    return bestBall

def draw_overlay(display_frame, ball):
    if ball is None:
        cv2.putText(display_frame, "no_ball_detected", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        return 
    x, y = ball.getX(), ball.getY()
    color = (0, 0, 255)
    cv2.circle(display_frame, (x, y), 8, color, 2)



cap = cv2.VideoCapture("IMG_3369 2.mov")
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    processed_frame = is_moving(gray)
    ball = detectBall(gray)
    print(ball)
    display = frame.copy()
    draw_overlay(display, ball)
    cv2.imshow("frame", display)

    if ball is not None:
        x, y, r, id, circ = int(ball.getX()), int(ball.getY()), int(ball.getRadius()), int(ball.getId()), (ball.getCircularity())
        cv2.circle(frame, (x, y), r, (0, 0, 255), 2)  # draw on the color frame so it's visible
        print(x, y, r, id, circ)

    if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
cap.release()
cv2.destroyAllWindows()
