import cv2
import numpy as np
import math
from ballObject import TennisBall

def detectBall(frame):
    possibleBalls = []
    _, transformToBinary = cv2.threshold(frame, 180, 255, cv2.THRESH_BINARY)
    kernel = np.ones((3,3), np.uint8)
    reduceNoiseFrame = cv2.morphologyEx(transformToBinary, cv2.MORPH_OPEN, kernel)
    reduceNoiseFrame = cv2.morphologyEx(transformToBinary, cv2.MORPH_CLOSE, kernel)

    contours, _ = cv2.findContours(reduceNoiseFrame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    focal_length_px = (1920 / 2) / math.tan((120/2))

    
    bestBall = None
    for contour in contours:
        areaOfTarget = cv2.contourArea(contour)

        if areaOfTarget < 300 and areaOfTarget > 10:
            circumference = cv2.arcLength(contour, True)
            if circumference > 0:
                circularity = (4*math.pi*areaOfTarget)/ (circumference**2)
                (x, y), (width, height), angle = cv2.minAreaRect(contour)
                estimated_diameter = min(width, height)
                aspect_ratio = max(width, height)/min(width, height)
                distance = 12
                rad = (0.067*focal_length_px) / distance
                if circularity > 0.9:
                    if (rad < 4.8) and (rad > 0.8):
                        possibleBall = TennisBall(x, y, rad, contour, circularity)
                        possibleBalls.append(possibleBall)

    print(possibleBalls)

    if len(possibleBalls) > 1:
        closestToOne = possibleBalls[0].getCircularity()
        bestBall = possibleBalls[0]
        for i in range(1, len(possibleBalls)):
            initialCircularity = possibleBalls[i].getCircularity()
            if (initialCircularity > closestToOne):
                closestToOne = initialCircularity
                bestBall = possibleBalls[i]

        return bestBall

    elif len(possibleBalls) == 1:
        bestBall = possibleBalls[0]
        return bestBall
    
    else:
        return bestBall
    

cap = cv2.VideoCapture('IMG_0330.MOV')

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # skip if footage is already mono

    ball = detectBall(gray)  # <-- this is the call

    if ball is not None:
        x, y, r, c = int(ball.getX()), int(ball.getY()), int(ball.getRadius()), (ball.getCircularity())
        print(x, y, r, c)
        cv2.circle(frame, (x, y), r, (0, 0, 255), 2)  # draw on the color frame so it's visible
    cv2.imshow("frame", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()