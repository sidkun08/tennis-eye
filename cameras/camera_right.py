import threading
import time
from collections import deque
from queue import Queue

try:
    from picamera2 import Picamera2
    _PICAMERA2_AVAILABLE = True
except ImportError:
    Picamera2 = None
    _PICAMERA2_AVAILABLE = False


# OV9281 is a 1280x800 mono sensor. Adjust CAPTURE_SIZE if your mode differs.
# "RGB888" is delivered as an OpenCV-friendly 3-channel array.
CAMERA_NUM = 1
CAPTURE_SIZE = (1280, 800)
FPS_WINDOW = 120

rightCamFrameQueue = Queue()

_stop_event = threading.Event()
_stopped = threading.Event()
_stopped.set()
_camera = None
_frame_times = deque(maxlen=FPS_WINDOW)
_fps = 0.0


def get_right_camera_fps():
    """Latest capture-rate estimate in frames per second (0.0 until known)."""
    return _fps


def _create_camera():
    camera = Picamera2(camera_num=CAMERA_NUM)
    config = camera.create_video_configuration(
        main={"size": CAPTURE_SIZE, "format": "RGB888"},
    )
    camera.configure(config)
    return camera


def _update_fps(timestamp):
    global _fps
    _frame_times.append(timestamp)
    if len(_frame_times) < 10:
        return
    span = _frame_times[-1] - _frame_times[0]
    if span > 0:
        _fps = (len(_frame_times) - 1) / span


def start_right_camera():
    """Capture into rightCamFrameQueue until stop_right_camera() is called."""
    global _camera
    _stopped.clear()
    if _stop_event.is_set():
        _stopped.set()
        return
    if not _PICAMERA2_AVAILABLE:
        print("[camera_right] picamera2 is not available; right camera disabled")
        _stopped.set()
        return

    try:
        _camera = _create_camera()
        _camera.start()
    except Exception as exc:
        print(f"[camera_right] failed to start: {exc}")
        _camera = None
        _stopped.set()
        return

    try:
        while not _stop_event.is_set():
            frame = _camera.capture_array("main")
            timestamp = time.monotonic()
            _update_fps(timestamp)
            rightCamFrameQueue.put((timestamp, frame))
    except Exception as exc:
        if not _stop_event.is_set():
            print(f"[camera_right] capture stopped: {exc}")
    finally:
        try:
            _camera.stop()
        except Exception:
            pass
        try:
            _camera.close()
        except Exception:
            pass
        _camera = None
        _stopped.set()


def stop_right_camera(timeout=2.0):
    """Ask the capture loop to exit and wait briefly for the camera to close."""
    _stop_event.set()
    _stopped.wait(timeout)
