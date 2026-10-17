"""Line decisions for a bounce point.

Singles only. Takes a bounce either as court coordinates (meters, origin at the center of
the net) or as an undistorted-image pixel plus that camera's homography.
Returns IN, OUT or UNCERTAIN; score_manager.apply_line_call() takes the
string directly.

Geometry comes from court_model.py, pixel conversion from
coordinate_transform.py. Nothing here knows court dimensions or matrix math.
"""
from typing import NamedTuple

import numpy as np

from court_model import CourtModel
from coordinate_transform import image_to_court, reprojection_errors

BALL_RADIUS_M = 0.0335     # a ball is IN if any part of it touches the line
DEFAULT_ERROR_M = 0.05     # PLACEHOLDER: replace with error_margin_from_landmarks()


class LineDecision(NamedTuple):
    call: str          # "IN", "OUT" or "UNCERTAIN"
    margin_m: float    # + = ball center inside the nearest line, - = outside
    boundary: str      # name of the nearest line


# ---------- helpers ----------

def _extract_xy(coords):
    arr = np.asarray(coords, dtype=float).ravel()
    if arr.size != 2 or not np.all(np.isfinite(arr)):
        raise ValueError(f"Expected one finite (x, y) point, got {coords!r}")
    return float(arr[0]), float(arr[1])


def _signed_margin(court, edges, x, y):
    """Distance to the nearest edge: positive inside the area, negative outside.

    Euclidean distance, so near a corner it measures to the corner itself
    rather than along each axis separately.
    """
    distances = {name: court.distance_to_line(x, y, seg) for name, seg in edges.items()}
    boundary = min(distances, key=distances.get)

    vertices = [seg[0] for seg in edges.values()]
    inside = court.point_in_boundary(x, y, vertices)

    d = distances[boundary]
    return (d if inside else -d), boundary


def _decide(margin, boundary, ball_radius, error_margin):
    effective = margin + ball_radius       # ball edge vs the line's outer edge
    if effective > error_margin:
        call = "IN"
    elif effective < -error_margin:
        call = "OUT"
    else:
        call = "UNCERTAIN"
    return LineDecision(call, margin, boundary)


def error_margin_from_landmarks(H, landmark_pixels, landmark_court,
                                safety_factor=1.5):
    """Derive error_margin from landmarks that were NOT used to build H.

    Uses coordinate_transform.reprojection_errors(). The worst error times a
    safety factor is a conservative, simple choice. Error grows with distance
    from the camera, so include far-side landmarks.
    """
    errors = reprojection_errors(H, landmark_pixels, landmark_court)
    return float(errors.max() * safety_factor)


# ---------- court-coordinate entry points ----------

def rally_call(court_xy, *, court=None,
               ball_radius=BALL_RADIUS_M, error_margin=DEFAULT_ERROR_M):
    court = court or CourtModel()
    x, y = _extract_xy(court_xy)
    margin, boundary = _signed_margin(court, court.boundary_edges(), x, y)
    return _decide(margin, boundary, ball_radius, error_margin)


def serve_call(court_xy, lane, net_side, *, court=None,
               ball_radius=BALL_RADIUS_M, error_margin=DEFAULT_ERROR_M):
    """lane / net_side: +1 or -1; which service box the ball must land in."""
    court = court or CourtModel()
    x, y = _extract_xy(court_xy)
    margin, boundary = _signed_margin(court, court.service_box_edges(lane, net_side), x, y)
    return _decide(margin, boundary, ball_radius, error_margin)


# ---------- pixel entry points (what main.py calls) ----------

def rally_call_from_pixel(H, bounce_pixel, **kwargs):
    """bounce_pixel: the bounce in the UNDISTORTED image of the camera that owns H."""
    return rally_call(image_to_court(H, bounce_pixel), **kwargs)


def serve_call_from_pixel(H, bounce_pixel, lane, net_side, **kwargs):
    return serve_call(image_to_court(H, bounce_pixel), lane, net_side, **kwargs)