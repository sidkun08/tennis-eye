import cv2
import numpy as np

court_boundaries = np.array([["x1", "y1"],
                             ["x2", "y2"],
                             ["x3", "y3"],
                             ["x4", "y4"]], dtype=np.int32) # TODO: Once obtained true camera film, with corners, will repalce placeholders.

def create_court_mask(frame_shape, polygon_points):
    h, w = frame_shape[:2]
    mask = np.zeros((h, w), dtype=np.uint8)
    cv2.fillPoly(mask, [polygon_points], 255)
    return mask

fgbg_left = cv2.createBackgroundSubtractorMOG2(history=200, detectShadows=False, varThreshold=16)
fgbg_right = cv2.createBackgroundSubtractorMOG2(history=200, detectShadows=False, varThreshold=16)

def gated_mask(frame, fgbg, court_mask):
    fg_mask = fgbg.apply(frame)
    gated_fgmask = cv2.bitwise_and(fg_mask, fg_mask, mask=court_mask)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    gated_fgmask = cv2.morphologyEx(gated_fgmask, cv2.MORPH_OPEN, kernel)
    processed = cv2.bitwise_and(frame, frame, mask=gated_fgmask)

    return processed
