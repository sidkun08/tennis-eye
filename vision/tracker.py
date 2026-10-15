import cv2
from trackerClass import Tracker
from detector import detectBall
import numpy as np

def flight_path(tracker, ball):
    if ball is not None:
        ball_coords = (ball.getX(), ball.getY())
        check = isMoving(tracker)
        if check == True:
            tracker.update(ball_coords)
            return {"positions": tracker.getTrajectory(),
            "current_position": tracker.getCurrent(),
            "velocity": tracker.getVelocity(),
            "missed_frames": tracker.getMissedFrames(),
            "id": ball.getId()
            }
    else:
        tracker.update(None)
        tracker.predict()


def isMoving(tracker):
    prev = tracker.getPrevious()
    curr = tracker.getCurrent()
    if prev is not None and curr is not None:
        diff_x = abs(prev[0] - curr[0])
        diff_y = abs(prev[1] - curr[1])

        if (diff_x < 100):
            if (diff_y > 100):
                return False
        return True

    return 
