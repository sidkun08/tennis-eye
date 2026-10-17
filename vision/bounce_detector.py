from dataclasses import dataclass
import math
import numpy as np


# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------
@dataclass
class BounceConfig:
    fps: float = 60.0                 # video frame rate
    metres_per_pixel: float =  0.01   # scene scale at the ball's depth (CALIBRATE!)

    # Tennis ball / air constants (SI)
    g: float = 9.81
    rho: float = 1.2                  # air density, kg/m^3
    ball_radius: float = 0.0327       # m
    ball_mass: float = 0.0577         # kg

    # Detection thresholds
    window: int = 15                  # most recent trajectory points examined
    min_points: int = 5
    min_vy: float = 1.0               # px/frame, ignore reversals smaller than this
    min_impulse: float = 3.0          # px/frame, min deviation from the flight model
    min_restitution: float = 0.15     # |vy_out| / |vy_in| plausible range
    max_restitution: float = 1.0
    max_cl: float = 0.45              # C_L = S/(1+2S) saturates at 0.5, so clip below


# ----------------------------------------------------------------------
# Magnus effect
# ----------------------------------------------------------------------
def liftCoefficient(speed, omega, radius):
    """C_L = 1 / (2 + v/(r*w)) = S / (1 + 2S), with spin parameter S = r*w / v."""
    if speed <= 1e-9 or abs(omega) <= 1e-9:
        return 0.0
    S = radius * abs(omega) / speed
    return math.copysign(S / (1.0 + 2.0 * S), omega)


def magnusAcceleration(vx, vy, omega, cfg):
    """
    Magnus acceleration in PIXELS/FRAME^2, given pixel velocity (px/frame)
    and spin omega (rad/s, + = topspin).

    Force direction: perpendicular to velocity, pointing downward for topspin
    regardless of whether the ball travels left or right.
    """
    scale = cfg.metres_per_pixel * cfg.fps           # px/frame -> m/s
    speed_px = math.hypot(vx, vy)
    if speed_px < 1e-9:
        return 0.0, 0.0
    speed = speed_px * scale
    C_L = liftCoefficient(speed, omega, cfg.ball_radius)
    area = math.pi * cfg.ball_radius ** 2
    a_mag = 0.5 * cfg.rho * C_L * area * speed ** 2 / cfg.ball_mass   # m/s^2

    side = 1.0 if vx >= 0 else -1.0
    ux, uy = side * (-vy) / speed_px, side * vx / speed_px            # unit perp
    k = 1.0 / (cfg.metres_per_pixel * cfg.fps ** 2)                   # m/s^2 -> px/frame^2
    return a_mag * ux * k, a_mag * uy * k


def estimateSpin(preVel, cfg):
    """
    Estimate spin (rad/s, + = topspin) from pre-bounce per-frame velocities.

    Any vertical acceleration beyond gravity is attributed to the Magnus force
    (air drag is ignored), then the lift equation is inverted for omega.
    Returns 0.0 if there isn't enough data.
    """
    if len(preVel) < 3:
        return 0.0

    acc = np.diff(preVel, axis=0)
    ay_obs = float(np.mean(acc[:, 1]))                      # px/frame^2
    g_px = cfg.g / (cfg.metres_per_pixel * cfg.fps ** 2)
    ay_magnus_px = ay_obs - g_px

    vx, vy = np.mean(preVel[:, 0]), np.mean(preVel[:, 1])
    speed_px = math.hypot(vx, vy)
    if speed_px < 1e-9:
        return 0.0

    # vertical component of the unit perpendicular (see magnusAcceleration)
    side = 1.0 if vx >= 0 else -1.0
    perp_y = side * vx / speed_px
    if abs(perp_y) < 0.2:       # ball moving nearly vertically: spin unobservable
        return 0.0

    a_mag = (ay_magnus_px / perp_y) * cfg.metres_per_pixel * cfg.fps ** 2   # m/s^2
    speed = speed_px * cfg.metres_per_pixel * cfg.fps
    area = math.pi * cfg.ball_radius ** 2

    C_L = 2.0 * cfg.ball_mass * a_mag / (cfg.rho * area * speed ** 2)
    sign = 1.0 if C_L >= 0 else -1.0
    C_L = min(abs(C_L), cfg.max_cl)
    S = C_L / (1.0 - 2.0 * C_L)                             # invert C_L = S/(1+2S)
    return sign * S * speed / cfg.ball_radius


# ----------------------------------------------------------------------
# Bounce location refinement
# ----------------------------------------------------------------------
def _refineBounce(pts, k):
    """
    Fit a line through the points before and after the vertex index k
    (parametrised by frame index) and intersect them. That gives the sub-frame
    ground-contact point instead of just the nearest sampled point.
    """
    pre = pts[max(0, k - 3):k]
    post = pts[k + 1:k + 4]
    fallback = (float(pts[k][0]), float(pts[k][1]))
    if len(pre) < 2 or len(post) < 2:
        return fallback

    tPre = np.arange(max(0, k - 3), k)
    tPost = np.arange(k + 1, k + 1 + len(post))

    axPre, bxPre = np.polyfit(tPre, pre[:, 0], 1)
    ayPre, byPre = np.polyfit(tPre, pre[:, 1], 1)
    axPost, bxPost = np.polyfit(tPost, post[:, 0], 1)
    ayPost, byPost = np.polyfit(tPost, post[:, 1], 1)

    denom = ayPre - ayPost
    if abs(denom) < 1e-9:
        return fallback

    t = (byPost - byPre) / denom
    t = min(max(t, k - 1), k + 1)                           # stay near the vertex
    x = 0.5 * ((axPre * t + bxPre) + (axPost * t + bxPost))
    y = 0.5 * ((ayPre * t + byPre) + (ayPost * t + byPost))
    return (float(x), float(y))


# ----------------------------------------------------------------------
# Main detector
# ----------------------------------------------------------------------
def detectBounce(tracker, cfg=None):
    """
    Returns (x, y) pixel coordinates of the most recent bounce in the tracker's
    trajectory, or None if no bounce is found.

    Uses tracker.getTrajectory() for positions and tracker.getVelocity()
    to confirm the ball is currently travelling upward.
    """
    cfg = cfg or BounceConfig()

    traj = tracker.getTrajectory()[-cfg.window:]
    if len(traj) < cfg.min_points:
        return None

    pts = np.asarray(traj, dtype=float)
    vel = np.diff(pts, axis=0)               # vel[i] = pts[i+1] - pts[i]
    vy = vel[:, 1]

    # Tracker's latest velocity must be upward (or at least not still falling)
    # for a bounce to have already happened.
    if tracker.getVelocity()[1] > cfg.min_vy:
        return None

    g_px = cfg.g / (cfg.metres_per_pixel * cfg.fps ** 2)

    # Newest candidate first. pts[k] is the vertex between vel[k-1] and vel[k].
    for k in range(len(vel) - 1, 0, -1):
        vIn, vOut = vy[k - 1], vy[k]

        # 1. Down -> up reversal. In free flight vy can only go up->down
        #    (gravity), so this flip is essentially unique to a bounce.
        if not (vIn > cfg.min_vy and vOut < -cfg.min_vy):
            continue

        # 2. Compare against the flight model (gravity + Magnus from the
        #    spin estimated on the approach). Topspin makes the ball dive,
        #    so the *expected* incoming vy is larger than gravity alone.
        omega = estimateSpin(vel[:k], cfg)
        amx, amy = magnusAcceleration(vel[k - 1][0], vIn, omega, cfg)
        vyPred = vIn + g_px + amy            # what flight physics predicts
        impulse = vyPred - vOut              # extra change = ground contact
        if impulse < cfg.min_impulse:
            continue

        # 3. Plausible coefficient of restitution (rejects tracker jitter).
        e = -vOut / vIn
        if not (cfg.min_restitution <= e <= cfg.max_restitution):
            continue

        return _refineBounce(pts, k)

    return None


class BounceDetector:
    """
    Stateful wrapper: call update(tracker) every frame and it returns the
    bounce coordinates once per bounce (None on all other frames).
    """

    def __init__(self, cfg=None):
        self.cfg = cfg or BounceConfig()
        self._lastBounce = None

    def update(self, tracker):
        bounce = detectBounce(tracker, self.cfg)
        if bounce is None:
            return None
        if self._lastBounce is not None:
            if math.hypot(bounce[0] - self._lastBounce[0],
                          bounce[1] - self._lastBounce[1]) < 15:
                return None                  # same bounce already reported
        self._lastBounce = bounce
        return bounce

    def reset(self):
        self._lastBounce = None