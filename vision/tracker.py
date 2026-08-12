import cv2
from trackerClass import Tracker
from detector import detectBall, changeObj
import time
def flight_path(tracker, ball):
    if ball is not None:
        tracker.update((ball.getX(), ball.getY()))

    else:
        tracker.update(None)
        tracker.predict()

    return {"positions": tracker.getTrajectory(),
                "current_position": tracker.getCurrent(),
                "velocity": tracker.findVelocity(),
                "missed_frames": tracker.getMissedFrames()
                }

def checkForTrajectory(tracker):
    trajectories = tracker.getTrajectory()
    length = len(trajectories)
    if length > 3:
        prev_x, prev_y = trajectories[length-2]
        curr_x, curr_y = trajectories[length-1]
        print(curr_x)
        diff_x = abs(prev_x - curr_x)
        if diff_x > 100:
            print("yo")
            trajectories.remove(trajectories[length-1])

 

def draw_overlay(display_frame, result):
    if result is None or result.get("current_position") is None:
        cv2.putText(display_frame, "no ball", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        return
 
    x, y = int(result["current_position"][0]), int(result["current_position"][1])
    color = (0, 0, 255)  # orange vs green (BGR)
    cv2.circle(display_frame, (x, y), 8, color, 2)
 
    label = "detected"
    vx, vy = result.get("velocity")
    missed = result.get("missed_frames")
    cv2.putText(display_frame, f"{label}  vel=({vx:.1f},{vy:.1f})  missed={missed}",
                (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
 

cap = cv2.VideoCapture("IMG_0386.MOV")
tracker = Tracker()
count = 0
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # skip if footage is already mono

    ball = detectBall(gray)
    tracking = flight_path(tracker, ball)
    count += 1
    checkForTrajectory(tracker)

    
    display_frame = frame.copy()
    draw_overlay(display_frame, tracking)
    
    cv2.imshow("Tracking test", display_frame)

    if ball is not None:
        x, y, r, id, circ = int(ball.getX()), int(ball.getY()), int(ball.getRadius()), int(ball.getId()), (ball.getCircularity())
        cv2.circle(frame, (x, y), r, (0, 0, 255), 2)  # draw on the color frame so it's visible
        print(x, y, r, id, circ)
        
    if cv2.waitKey(200) & 0xFF == ord('q'):
        break
        
cap.release()
cv2.destroyAllWindows()
