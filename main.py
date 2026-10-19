"""
Main entry point for TennisEye VAR.

Connects the existing camera streams, ball detection/tracking, bounce
detection, court homography, line decisions, scoring, event logging, and
scoreboard UI into one pipeline. Only functions already present in the
project modules are used here.

Run from the project root:
    python main.py
"""

import os
import sys
import time
import threading
import importlib
from queue import Empty

# The project modules import their siblings by bare name (for example
# detector.py imports "ballObject", line_decision.py imports "court_model").
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
for _path in (
    PROJECT_ROOT,
    os.path.join(PROJECT_ROOT, "vision"),
    os.path.join(PROJECT_ROOT, "scoring"),
    os.path.join(PROJECT_ROOT, "court"),
):
    if _path not in sys.path:
        sys.path.insert(0, _path)

import cv2
import numpy as np

# ---- Cameras ---------------------------------------------------------
from cameras.camera_left import start_left_camera, leftCamFrameQueue, leftCamera
from cameras.camera_right import start_right_camera, rightCamFrameQueue, rightCamera

# ---- Vision ----------------------------------------------------------
from vision.detector import detectBall
from vision.trackerClass import Tracker
from vision.tracker import flight_path
from vision.bounce_detector import BounceDetector

# ---- Court -----------------------------------------------------------
from court.court_model import CourtModel
from court.coordinate_transform import build_homography, reprojection_errors
from court.line_decision import rally_call_from_pixel, error_margin_from_landmarks

# ---- Scoring ---------------------------------------------------------
from scoring.score_manager import ScoreManager

# ---- UI --------------------------------------------------------------
from ui.display import run_app

# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------
# Calibration landmarks: clicked court corners in each camera's image,
# in the same order as the real-world points below.
LEFT_IMG_COORDS = [[100, 100], [540, 100], [580, 420], [60, 420]] # placeholder coords
RIGHT_IMG_COORDS = [[100, 100], [540, 100], [580, 420], [60, 420]] # placeholder coords

BEST_OF_SETS = 3
PLAYER_NAME = "Player"
OPPONENT_NAME = "Opponent"


# ---------------------------------------------------------------------
# Court model + homographies (one per camera) and a conversion sanity check
# ---------------------------------------------------------------------
court_model = CourtModel()
COURT_CORNERS = court_model.court_corners()

def main():
        
    camera_config = {
        "left": {"queue": leftCamFrameQueue, "image_coords": LEFT_IMG_COORDS},
        "right": {"queue": rightCamFrameQueue, "image_coords": RIGHT_IMG_COORDS},
    }

    for name, cfg in camera_config.items():
        try:
            _H, _ = build_homography(cfg["image_coords"], COURT_CORNERS)
            cfg["H"] = _H
            _errors = reprojection_errors(_H, cfg["image_coords"], COURT_CORNERS)
            cfg["error_margin"] = error_margin_from_landmarks(
                _H, cfg["image_coords"], COURT_CORNERS
            )
            print(
                f"Calibration [{name}] max landmark error: "
                f"{float(np.max(_errors)):.4f} m, error margin: {cfg['error_margin']:.4f} m"
            )
        except Exception as _exc:
            cfg["H"] = None
            cfg["error_margin"] = None
            print(f"Calibration [{name}] failed: {_exc}")


    # ---------------------------------------------------------------------
    # Start both camera streams (existing start_*_camera functions)
    # ---------------------------------------------------------------------
    threading.Thread(target=start_left_camera, daemon=True).start()
    threading.Thread(target=start_right_camera, daemon=True).start()


    # ---------------------------------------------------------------------
    # Vision state
    # ---------------------------------------------------------------------
    trackers = {"left": Tracker(), "right": Tracker()}
    bounce_detectors = {"left": BounceDetector(), "right": BounceDetector()}


    # ---------------------------------------------------------------------
    # UI + scoring (window.update_score is the score-change callback)
    # ---------------------------------------------------------------------
    app, window = run_app("Tennis VAR - Scoreboard")
    score_manager = ScoreManager(
        on_score_change=window.update_score,
        player_name=PLAYER_NAME,
        opponent_name=OPPONENT_NAME,
        best_of_sets=BEST_OF_SETS,
    )


    # ---------------------------------------------------------------------
    # Main loop
    # ---------------------------------------------------------------------
    print("TennisEye VAR running. Close the scoreboard window or press Ctrl+C to quit.")

    try:
        while window.isVisible():
            app.processEvents()

            for name, cfg in camera_config.items():
                queue = cfg["queue"]

                # Keep only the newest frame.
                frame = None
                while True:
                    try:
                        _timestamp, frame = queue.get_nowait()
                    except Empty:
                        break

                if frame is None:
                    continue

                # Ball detection + tracking
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                ball = detectBall(gray)
                if ball is None:
                    trackers[name].update(None)
                    continue

                flight_path(trackers[name], ball)

                # Bounce detection
                bounce = bounce_detectors[name].update(trackers[name])
                if not bounce:
                    continue

                window.update_decision_status(None)

                # Court homography -> line decision
                if cfg["H"] is None:
                    print(f"[{name}] bounce {bounce} ignored (no homography)")
                    continue

                line = rally_call_from_pixel(
                    cfg["H"], bounce, error_margin=cfg["error_margin"]
                )
                print(
                    f"[{name}] bounce {bounce} -> {line.call} "
                    f"({line.boundary}, margin {line.margin_m:+.3f} m)"
                )

                window.update_decision_status(line.call)

                # Award a point only on an OUT call.
                if line.call == "OUT":
                    hitter = "player" if name == "left" else "opponent"
                    score_manager.handleline_call(is_out=True, hitter=hitter)

            time.sleep(0.005)

    except KeyboardInterrupt:
        print("\nInterrupted.")

    finally:
        leftCamera.release()
        rightCamera.release()
        cv2.destroyAllWindows()
        print("Shutdown complete.")

if __name__ == "__main__":
    main()