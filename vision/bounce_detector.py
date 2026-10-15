"""Bounce detection with Magnus-effect-aware trajectory handling.

This module works from tracker trajectory and velocity data. It detects a
bounce when the ball's vertical motion reverses, estimates spin when it is
not supplied, and provides Magnus-aware motion helpers for refining or
predicting the ball's path.
"""

import math


# Small values used to avoid division by zero and ambiguous detections.
_MIN_SPEED = 1e-6
_MIN_VERTICAL_VELOCITY = 1.0
_DEFAULT_DT = 1.0 / 30.0


def _as_point(value):
    if isinstance(value, dict):
        return float(value.get("x", 0.0)), float(value.get("y", 0.0))
    if hasattr(value, "getX") and hasattr(value, "getY"):
        return float(value.getX()), float(value.getY())
    return float(value[0]), float(value[1])


def _get_trajectory(tracker):
    """Read a trajectory list from several compatible tracker interfaces."""
    for method_name in ("getTrajectory", "get_trajectory", "getTrajectoryPoints"):
        method = getattr(tracker, method_name, None)
        if callable(method):
            try:
                return list(method())
            except Exception:
                pass

    for attr_name in ("trajectory", "positions", "_trajectory"):
        value = getattr(tracker, attr_name, None)
        if value is not None and not callable(value):
            try:
                return list(value)
            except Exception:
                pass

    return []


def _get_velocity(tracker):
    """Read a velocity pair from several compatible tracker interfaces."""
    for method_name in ("getVelocity", "get_velocity"):
        method = getattr(tracker, method_name, None)
        if callable(method):
            try:
                velocity = method()
                if velocity is not None:
                    return float(velocity[0]), float(velocity[1])
            except Exception:
                pass

    for attr_name in ("velocity", "_velocity"):
        value = getattr(tracker, attr_name, None)
        if isinstance(value, (tuple, list)) and len(value) >= 2:
            try:
                return float(value[0]), float(value[1])
            except Exception:
                pass

    trajectory = _get_trajectory(tracker)
    if len(trajectory) >= 2:
        previous = _as_point(trajectory[-2])
        current = _as_point(trajectory[-1])
        return current[0] - previous[0], current[1] - previous[1]

    return None


def _safe_norm(value_x, value_y):
    return math.hypot(value_x, value_y)


def estimate_spin(trajectory, dt=_DEFAULT_DT):
    """Estimate a scalar spin value from recent trajectory curvature."""
    points = [_as_point(point) for point in trajectory]
    if len(points) < 3:
        return 0.0

    previous = points[-3]
    middle = points[-2]
    current = points[-1]

    v1_x = middle[0] - previous[0]
    v1_y = middle[1] - previous[1]
    v2_x = current[0] - middle[0]
    v2_y = current[1] - middle[1]

    if dt <= 0:
        dt = _DEFAULT_DT

    ax = (v2_x - v1_x) / (dt * dt)
    ay = (v2_y - v1_y) / (dt * dt)

    speed = _safe_norm(v1_x, v1_y)
    if speed < _MIN_SPEED:
        return 0.0

    cross = v1_x * ay - v1_y * ax
    curvature = cross / (speed ** 3 + _MIN_SPEED)

    return curvature * speed * speed


def magnus_acceleration(
    velocity_x,
    velocity_y,
    spin,
    gravity=9.81,
    magnus_coefficient=0.02,
    drag=0.0,
):
    """Return (ax, ay) including gravity, Magnus, and optional drag."""
    speed = _safe_norm(velocity_x, velocity_y)

    magnus_x = magnus_coefficient * spin * (-velocity_y)
    magnus_y = magnus_coefficient * spin * velocity_x

    drag_x = -drag * velocity_x * speed
    drag_y = -drag * velocity_y * speed

    ax = magnus_x + drag_x
    ay = gravity + magnus_y + drag_y
    return ax, ay


def predicted_motion(
    start_x,
    start_y,
    velocity_x,
    velocity_y,
    spin=0.0,
    dt=_DEFAULT_DT,
    steps=100,
    gravity=9.81,
    magnus_coefficient=0.02,
    drag=0.0,
):
    """Integrate the ball path using gravity and Magnus forces."""
    if dt <= 0:
        dt = _DEFAULT_DT

    x = float(start_x)
    y = float(start_y)
    vx = float(velocity_x)
    vy = float(velocity_y)
    path = []

    for _ in range(max(1, steps)):
        ax, ay = magnus_acceleration(
            vx,
            vy,
            spin,
            gravity=gravity,
            magnus_coefficient=magnus_coefficient,
            drag=drag,
        )
        vx += ax * dt
        vy += ay * dt
        x += vx * dt
        y += vy * dt
        path.append((x, y))

    return path


def detect_vertical_reversal(
    trajectory, velocity, min_vertical_velocity=_MIN_VERTICAL_VELOCITY
):
    """Return True when vertical motion changes from downward to upward."""
    if len(trajectory) < 3 or velocity is None:
        return False

    previous_vertical_velocity = _as_point(trajectory[-2])[1] - _as_point(trajectory[-3])[1]
    current_vertical_velocity = velocity[1]

    return (
        previous_vertical_velocity > min_vertical_velocity
        and current_vertical_velocity < -min_vertical_velocity
    )


def bounce_detect(
    tracker,
    spin=None,
    min_vertical_velocity=_MIN_VERTICAL_VELOCITY,
    gravity=9.81,
    magnus_coefficient=0.02,
    drag=0.0,
    refine_with_magnus=True,
):
    """Detect a bounce from tracker data."""
    trajectory = _get_trajectory(tracker)
    velocity = _get_velocity(tracker)

    if len(trajectory) < 2 or velocity is None:
        return None

    reported_length = getattr(tracker, "_bounce_detector_reported_length", -1)
    if len(trajectory) == reported_length:
        return None

    points = [_as_point(point) for point in trajectory]

    if len(points) >= 3:
        previous_vertical_velocity = points[-2][1] - points[-3][1]
        is_bounce = (
            previous_vertical_velocity > min_vertical_velocity
            and velocity[1] < -min_vertical_velocity
        )
    else:
        is_bounce = velocity[1] < -min_vertical_velocity and abs(velocity[1]) > min_vertical_velocity

    if not is_bounce:
        return None

    contact_point = points[-2]
    bounce_x, bounce_y = contact_point

    if spin is None:
        spin = estimate_spin(trajectory)

    if refine_with_magnus and len(points) >= 3:
        previous_point = points[-3]
        current_point = points[-1]
        observed_dx = current_point[0] - previous_point[0]
        velocity_x = velocity[0]

        if abs(velocity_x) > _MIN_SPEED:
            predicted_positions = predicted_motion(
                contact_point[0],
                contact_point[1],
                velocity_x,
                velocity[1],
                spin=spin,
                dt=_DEFAULT_DT,
                steps=1,
                gravity=gravity,
                magnus_coefficient=magnus_coefficient,
                drag=drag,
            )
            if predicted_positions:
                predicted_x = predicted_positions[0][0]
                bounce_x = (bounce_x + predicted_x + observed_dx * 0.1) / 3.0

    try:
        setattr(tracker, "_bounce_detector_reported_length", len(trajectory))
    except Exception:
        pass

    return (float(bounce_x), float(bounce_y))