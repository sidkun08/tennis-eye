import numpy as np
import cv2

class CourtModel:
    def __init__(self):
        # Standard tennis court dimensions in meters
        # Origin (0,0) is placed at the center of the net
        self.half_length = 23.77 / 2  # 11.885m
        self.singles_half_width = 8.23 / 2  # 4.115m
        self.doubles_half_width = 10.97 / 2 # 5.485m
        
        self.homography_matrix = None

    def calibrate(self, image_points, court_points):
        """
        Calculates the transformation matrix.
        image_points: List of (x, y) pixel coordinates from the camera feed.
        court_points: List of corresponding (x, y) real-world coordinates in meters.
        (Requires a minimum of 4 points, e.g., net post and line intersections)
        """
        src_pts = np.array(image_points, dtype=np.float32).reshape(-1, 1, 2)
        dst_pts = np.array(court_points, dtype=np.float32).reshape(-1, 1, 2)
        
        # cv2.RANSAC filters out minor inaccuracies in manual point clicking
        self.homography_matrix, status = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
        
        return self.homography_matrix is not None

    def pixel_to_court_coord(self, pixel_x, pixel_y):
        """
        Warps a bounce pixel coordinate into a real-world metric coordinate.
        """
        if self.homography_matrix is None:
            raise ValueError("Court not calibrated. Run calibrate() first.")
            
        # Format for cv2 perspective transform
        pts = np.array([[[float(pixel_x), float(pixel_y)]]])
        real_world_pt = cv2.perspectiveTransform(pts, self.homography_matrix)
        
        return real_world_pt[0][0][0], real_world_pt[0][0][1]

    def is_in(self, bounce_x, bounce_y, match_type="singles"):
        """
        Determines if the calculated bounce coordinate is inbounds.
        Assumes x is the length of the court and y is the width.
        """
        # Check if length is past the baseline
        if abs(bounce_x) > self.half_length:
            return False
            
        # Check width based on match type
        max_width = self.singles_half_width if match_type == "singles" else self.doubles_half_width
        if abs(bounce_y) > max_width:
            return False
            
        return True