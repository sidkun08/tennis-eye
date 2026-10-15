import cv2
import numpy as np

PATTERN = (9, 6)
SQUARE_SIZE = 0.025
CRITERIA = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

objp = np.zeros((PATTERN[0] * PATTERN[1], 3), np.float32)
objp[:, :2] = np.mgrid[0:PATTERN[0], 0:PATTERN[1]].T.reshape(-1, 2) * SQUARE_SIZE

def calibrate(frames):
    obj_points, img_points = [], []

    for gray in frames:
        found, corners = cv2.findChessboardCorners(gray, PATTERN)
        if found:
            corners = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), CRITERIA)
            obj_points.append(objp)
            img_points.append(corners)

    h, w = frames[0].shape[:2]
    _, camera_matrix, dist_coeffs, _, _ = cv2.calibrateCamera(
        obj_points, img_points, (w, h), None, None
    )
    return camera_matrix, dist_coeffs