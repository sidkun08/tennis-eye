# Tennis Line-Calling System

An amateur tennis line-calling project built around a Raspberry Pi 5 and two OV9281 global-shutter monochrome cameras. The goal is to detect and track a tennis ball, estimate its bounce location, determine whether it landed in or out, and support match scorekeeping.

> **Project status:** In development. Features described as planned or in progress should not be considered complete until implemented and tested on the target hardware.

## Goals

- Capture frames from two cameras viewing different halves of the court.
- Detect and track the tennis ball across frames.
- Calibrate each camera and transform relevant bounce estimates into a shared court coordinate system.
- Estimate when and where the ball bounces.
- Evaluate IN/OUT calls against the applicable court boundaries.
- Support net-call logic and tennis scoring.
- Save event images and, eventually, display the score and camera feed on a screen.

## Hardware

Current target hardware:

- Raspberry Pi 5
- Two InnoMaker OV9281 monochrome global-shutter cameras
- Compatible camera cables and power supply
- Optional display for score and camera feed
- microSD card with Raspberry Pi OS

Check camera interface compatibility, driver support, ribbon-cable orientation, power requirements, and supported frame rates before assembly. High advertised camera frame rates do not guarantee that the full capture, detection, and tracking pipeline can sustain those rates on the Raspberry Pi.

## Software

Planned/considered software stack:

- Python 3
- OpenCV (`cv2`) for image processing and camera-frame operations
- NumPy for numerical operations
- SciPy for numerical utilities if needed
- FilterPy for Kalman filtering if used
- Shapely for geometric operations if needed
- PySide6 for a graphical display if implemented
- SQLite for event storage if implemented

Only install libraries that the current code actually imports. Camera capture dependencies may differ between Raspberry Pi OS versions and camera interfaces.

## Architecture

The system is divided into modules with separate responsibilities.

| Module | Responsibility |
|---|---|
| `main.py` | Coordinates the pipeline and connects modules. |
| `config.py` | Stores shared configuration, thresholds, and settings. |
| `camera_left.py` | Captures frames from the left-side camera. |
| `camera_right.py` | Captures frames from the right-side camera. |
| `preprocessing.py` | Performs image preprocessing, such as undistortion or filtering. |
| `detector.py` | Finds candidate ball detections in a frame. |
| `tracker.py` | Maintains ball position and motion estimates across frames. |
| `calibration.py` | Collects calibration points and calculates camera calibration data. |
| `court_model.py` | Defines court dimensions, boundaries, and named line segments in meters. |
| `coordinate_transform.py` | Maps image-plane points to shared court coordinates using each camera's calibration. |
| `bounce.py` | Estimates whether a bounce occurred and its likely location. |
| `line_decision.py` | Evaluates the estimated bounce against the relevant court boundary. |
| `net_call.py` | Evaluates possible net-contact events and reports them to the match logic. |
| `match_state.py` | Stores current match, set, game, point, and server state. |
| `scoring_rules.py` | Holds scoring-rule calculations. |
| `score_manager.py` | Applies confirmed point outcomes and updates match state. |
| `display.py` | Displays score and camera information if a UI is implemented. |
| `event_logger.py` | Records important events and saves event images if implemented. |

Some modules may not exist yet or may change as the design develops. Keep this table synchronized with the actual repository. A separate `fusion.py` is optional for the first version; add it only if tests show that combining observations from both cameras is useful.

## Coordinate System and Calibration

The court coordinate system uses meters, with the origin at the **center of the net on the court plane**:

- The `x` axis runs across the court.
- The `y` axis runs along the court.
- The court extends approximately 11.885 m from the net to either baseline.
- Singles court width is approximately 8.23 m.
- Doubles court width is approximately 10.97 m.

Each camera needs its own calibration because the cameras have different viewpoints. Each calibration maps image coordinates to the same shared court coordinate system.

**Important:** A planar homography is appropriate for points on the court plane. A ball in flight is above that plane, so directly transforming its image center with a court-plane homography can produce an inaccurate court location. The system should estimate the ball's ground-contact/bounce point or use a suitable 3D or trajectory model before making a line call.

## Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd <repository-folder>
```

Replace the placeholders with your repository URL and folder name.

### 2. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows, activate with:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

If the repository has a `requirements.txt` file:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Otherwise, create a requirements file based on the imports used by the current project. For example, if the code uses OpenCV and NumPy:

```bash
python -m pip install opencv-python numpy
```

On Raspberry Pi OS, camera capture may use the system's libcamera/Picamera2 stack. Follow the camera manufacturer's instructions and Raspberry Pi documentation for the specific camera interface. Avoid assuming a camera will work with `cv2.VideoCapture()` until its interface and driver are verified.

### 4. Configure the cameras

1. Connect each camera to the correct interface and check the cable orientation.
2. Confirm that the operating system detects the camera hardware.
3. Test each camera independently before running the full application.
4. Confirm stable frame capture and record the actual frame dimensions and frame rate.
5. Configure the left and right camera modules to use the correct device/interface settings.

## Running the Project

The intended entry point is `main.py`:

```bash
python main.py
```

This command will work once `main.py`, the camera modules, and their dependencies have been implemented and configured. If the current code is still in development, run and test each module independently first.

## Development Workflow

A practical implementation order is:

1. **Camera capture:** reliably capture frames from each camera.
2. **Preprocessing:** validate image quality and apply necessary filtering or lens correction.
3. **Ball detection:** identify candidate ball locations and tune false-positive handling.
4. **Tracking:** maintain a consistent ball track across frames and handle short detection gaps.
5. **Court calibration:** identify court landmarks and calculate a separate transform for each camera.
6. **Bounce estimation:** detect likely direction changes and estimate the contact point using multiple frames.
7. **Line decisions:** compare the estimated bounce location with the correct singles, doubles, or service boundary.
8. **Net and scoring logic:** handle possible net contacts and confirmed point outcomes.
9. **Logging and UI:** save event images and display results after the core pipeline is reliable.
10. **On-court testing:** evaluate accuracy under different lighting, ball speeds, camera angles, and occlusions.

## Testing

Test modules independently before relying on automatic calls in a live match.

- **Camera tests:** verify that both cameras produce frames consistently.
- **Detector tests:** check ball detections and false positives in recorded frames.
- **Tracker tests:** verify continuity and velocity estimates through short occlusions.
- **Calibration tests:** transform known court landmarks and measure their coordinate errors.
- **Bounce tests:** use recorded clips with known bounce locations and compare estimates.
- **Line-decision tests:** test points clearly inside, outside, and on each relevant line.
- **Scoring tests:** check deuce, advantage, tie-breaks, game/set transitions, and match completion.
- **Integration tests:** confirm that a single detected event does not accidentally award multiple points.

An automatic line call should be treated as a prediction until the system has been validated against a reliable ground truth. Log uncertain events for review rather than presenting unverified calls as guaranteed.

## Known Challenges

- Monochrome ball detection can produce false positives from court lines, reflections, and other bright objects.
- Camera driver or interface configuration may prevent frames from streaming.
- Calibration accuracy depends on visible, accurately identified court landmarks.
- A ball's image position does not directly give its ground-contact position when the ball is airborne.
- High frame rates increase processing and data-throughput demands.
- Net contact and bounces can be brief or partly occluded.
- Both cameras must use consistent court coordinates before their measurements can be compared.

## Current Status

Update this section as the project progresses.

- [ ] Reliable frame capture from both cameras
- [ ] Ball detection
- [ ] Persistent ball tracking
- [ ] Camera calibration
- [ ] Shared court coordinate mapping
- [ ] Bounce estimation
- [ ] IN/OUT decision logic
- [ ] Net-call handling
- [ ] Tennis scoring
- [ ] Event image logging
- [ ] Score and camera display
- [ ] On-court validation

## Safety and Usage Note

This is an experimental amateur system, not a certified officiating system. Use it as an aid during testing and recreational play, and agree with players in advance how uncertain calls will be handled.

## Contributing

Keep each module focused on one responsibility, document configuration changes, and test changes against recorded frames or match clips before using them on court.

## License

No license has been selected yet. Add a license before distributing the project publicly.
