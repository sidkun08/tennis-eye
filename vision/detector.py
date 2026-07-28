import cv2
import numpy as np
import math
from ballObject import TennisBall

def detectBall(frame):
    possibleBalls = []
    _, transformToBinary = cv2.threshold(frame, 180, 255, cv2.THRESH_BINARY)
    kernel = np.ones((3,3), np.uint8)
    # reduceNoiseFrame = cv2.morphologyEx(transformToBinary, cv2.MORPH_OPEN, kernel)
    reduceNoiseFrame = cv2.morphologyEx(transformToBinary, cv2.MORPH_CLOSE, kernel)

    contours, _ = cv2.findContours(reduceNoiseFrame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

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
                    if 0.8 < (min(width, height)/2) < 4.5:
                        possibleBall = TennisBall(cx, cy, radius, contour, circularity)
                        possibleBalls.append(possibleBall)     
                    else:
                        continue   
                elif 0.30 < circularity < 0.40:
                    aspectRatio = max(width, height) / min(width, height)
                    if 1.5 < aspectRatio < 4:
                        if 0.8 < (min(width, height)/2) < 4.5:
                            possibleBall = TennisBall(cx, cy, radius, contour, circularity)
                            possibleBalls.append(possibleBall)
                    else:
                        continue
            else:
                continue
    maxCircularity = 0
    bestBall = None
    if len(possibleBalls) > 1:
        for i in possibleBalls:
            circ = i.getCircularity()
            if circ > maxCircularity:
                maxCircularity = circ
                bestBall = i
    
    elif len(possibleBalls) == 1:
        bestBall = possibleBalls[0]
    
    return bestBall


cap = cv2.VideoCapture("IMG_0386.MOV")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # skip if footage is already mono

    ball = detectBall(gray)  # <-- this is the call

    if ball is not None:
        x, y, r = int(ball.getX()), int(ball.getY()), int(ball.getRadius())
        cv2.circle(frame, (x, y), r, (0, 0, 255), 2)  # draw on the color frame so it's visible
        print(x, y, r)

    cv2.imshow("frame", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()