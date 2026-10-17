"""Image <-> court coordinates for ONE camera.

Image points must be in the UNDISTORTED image (the frame preprocessing.py
returns). Court points are in meters, origin at the center of the net.

The homography is only valid for points ON the court surface, so apply it to
the bounce point, never to a ball in flight.
"""
import cv2
import numpy as np

# RANSAC measures error in the DESTINATION units. The court points are in
# meters, so this is meters. (5.0 would be five meters, which rejects nothing.)
DEFAULT_RANSAC_THRESHOLD_M = 0.10


def build_homography(image_points, court_points,
                     ransac_threshold_m=DEFAULT_RANSAC_THRESHOLD_M):
    """Build the matrix once per camera at setup. Returns (H, inlier_mask)."""
    src = np.asarray(image_points, dtype=np.float64).reshape(-1, 2)
    dst = np.asarray(court_points, dtype=np.float64).reshape(-1, 2)

    if len(src) != len(dst):
        raise ValueError("image_points and court_points must have the same length")
    if len(src) < 4:
        raise ValueError("Need at least 4 point pairs")

    # RANSAC needs spare points to find outliers; with exactly 4 use plain solve
    method = cv2.RANSAC if len(src) > 4 else 0
    H, mask = cv2.findHomography(src, dst, method, ransac_threshold_m)
    # Collinear points can return a singular matrix instead of None
    if H is None or np.linalg.matrix_rank(H) < 3:
        raise ValueError("Homography failed (points may be collinear or degenerate)")

    inliers = np.ones(len(src), dtype=bool) if mask is None or mask.size == 0 \
        else mask.ravel().astype(bool)
    return H, inliers


def image_to_court(H, points):
    """Convert one or more undistorted image points to court meters.

    Returns an array of shape (N, 2); one point gives shape (1, 2).
    """
    pts = np.asarray(points, dtype=np.float64).reshape(-1, 1, 2)
    return cv2.perspectiveTransform(pts, H).reshape(-1, 2)


def reprojection_errors(H, image_points, court_points):
    """Per-point error in meters. Use landmarks you did NOT build H from."""
    est = image_to_court(H, image_points)
    true = np.asarray(court_points, dtype=np.float64).reshape(-1, 2)
    return np.linalg.norm(est - true, axis=1)


def get_transformed_coords(img_coords, real_world_coords, bounce_coords):
    """Original one-shot interface. Rebuilds H on every call, so use
    build_homography() once and image_to_court() per bounce instead."""
    H, _ = build_homography(img_coords, real_world_coords)
    return image_to_court(H, bounce_coords)