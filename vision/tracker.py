import cv2
from trackerClass import Tracker
from detector import detectBall

def flight_path(tracker, ball):
    trajs = tracker.getTrajectory()
    if ball is not None:
        ball_coords = (ball.getX(), ball.getY())
        ball_id = ball.getId()
        tracker.update(ball_coords)
        tracker.track_continuity(ball_coords, ball_id)
        check = isMoving(trajs, ball)
        if check == True:
            return {"positions": tracker.getTrajectory(),
            "current_position": tracker.getCurrent(),
            "velocity": tracker.getVelocity(),
            "missed_frames": tracker.getMissedFrames(),
            "id": ball.getId()
            }
        else:
            tracker.update(None)
            tracker.predict()

def isMoving(trajectories, ball):
    prev = tracker.getPrevious()
    curr = tracker.getCurrent()
    if prev is not None and curr is not None:
        if (abs(prev[0] - curr[0]) < 5):
            if (abs(prev[1] - curr[1]) < 5):
                tracker.alter_trajectory(curr, prev, 1)
                return False
        return True

    return 

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


cap = cv2.VideoCapture("IMG_3369 2.mov")
tracker = Tracker()
count = 0
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # skip if footage is already mono
    ball = detectBall(gray)
    tracking = flight_path(tracker, ball)
    display_frame = frame.copy()
    draw_overlay(display_frame, tracking)
    
    cv2.imshow("Tracking test", display_frame)

    if ball is not None:
        x, y, r, id, circ = int(ball.getX()), int(ball.getY()), int(ball.getRadius()), int(ball.getId()), (ball.getCircularity())
        cv2.circle(frame, (x, y), r, (0, 0, 255), 2)  # draw on the color frame so it's visible
        print(x, y, r, id, circ)
        
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
        
cap.release()
cv2.destroyAllWindows()
