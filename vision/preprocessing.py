import cv2
import numpy as np

court_boundaries = np.array([["x1", "y1"],
                             ["x2", "y2"],
                             ["x3", "y3"],
                             ["x4", "y4"]], dtype=np.int32)

def create_court_mask(frame_shape, polygon_points):
    h, w = frame_shape[:2]
    mask = np.zeros((h, w), dtype=np.uint8)
    cv2.fillPoly(mask, [polygon_points], 255)
    return mask

court_mask = None
def gated_mask(frame, fgbg):
    global court_mask
    if court_mask is None:
        court_mask = create_court_mask(frame.shape, court_boundaries)

    fg_mask = fgbg.apply(frame)
    gated_fgmask = cv2.bitwise_and(fg_mask, fg_mask, mask=court_mask)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    gated_fgmask = cv2.morphologyEx(gated_fgmask, cv2.MORPH_OPEN, kernel)

    return gated_fgmask
