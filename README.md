# Tennis Line-Calling System

An amateur line-calling project built on a Raspberry Pi 5 and two OV9281 global-shutter cameras. It watches a tennis ball, works out where it bounced, and decides whether it was in or out. Scorekeeping comes along for the ride.

> **Status: work in progress.** Nothing here has been validated on a real court yet. Treat any feature as unfinished until it has been tested on the actual hardware.

## What it's meant to do

- Capture frames from two cameras, each watching one half of the court.
- Detect and track the ball across frames.
- Calibrate each camera and map bounce points into one shared court coordinate system.
- Find when and where the ball bounces.
- Call it IN, OUT, or UNCERTAIN against the right lines.
- Keep score, and handle net contacts later on.
- Save an image of each event and eventually show the score and camera feed on a screen.

I'm starting with **singles only**. Doubles can come once singles works.

## How it fits together

Each camera runs its own pipeline and shares nothing with the other:

```
camera -> preprocessing -> detector -> tracker -> bounce -> court coordinates -> line call -> score
```

Preprocessing undistorts the frame and blanks out everything that isn't moving inside the area of interest. The detector looks for ball-sized bright blobs in what's left. The tracker follows the ball between frames, and once a bounce is found its pixel position is converted to meters on the court and compared with the lines.

## Hardware

- Raspberry Pi 5
- Two InnoMaker OV9281 monochrome global-shutter cameras
- Matching cables and a decent power supply
- microSD card with Raspberry Pi OS
- Optional screen for the score and camera feed

Before you assemble anything, check which interface your cameras use, that the drivers exist for your OS version, the cable orientation, power draw, and the frame rates they really support. A camera that can do 300+ fps doesn't mean the Pi can capture, detect, and track at that rate, so expect to run slower and find the ceiling by testing.

## Software

- Python 3
- OpenCV (`cv2`) and NumPy for the core work
- PySide6 for the scoreboard window (if I build it)
- SQLite for event storage (if I build it)
- SciPy, FilterPy, and Shapely only if a module ends up needing them

Only install what the code actually imports. Camera access depends on the Pi OS version and the camera interface, so don't assume `cv2.VideoCapture()` will just work. Check that first.

## Project layout

| File | What it does |
|---|---|
| `main.py` | Runs the pipeline, one stage at a time (see below) |
| `config.py` | Shared thresholds and settings (planned; for now they live at the top of each file) |
| `camera_left.py`, `camera_right.py` | Capture frames from each camera into a queue |
| `preprocessing.py` | Undistortion, region-of-interest gating, motion filtering |
| `detector.py` | Finds ball candidates in a frame |
| `tracker.py`, `trackerClass.py` | Follows the ball across frames and picks the right candidate |
| `calibration.py` | Lens calibration from chessboard images |
| `court_model.py` | Court dimensions and line geometry, in meters |
| `coordinate_transform.py` | Image points to court coordinates, one matrix per camera |
| `bounce_detector.py` | Decides when a bounce happened and where |
| `line_decision.py` | IN / OUT / UNCERTAIN, taking ball radius and measurement error into account |
| `match_state.py`, `score_rules.py`, `score_manager.py` | Score data, scoring rules, and the code that applies line calls to the score |
| `net_call.py` | Net-contact handling (planned) |
| `display.py` | Scoreboard and feed display |

Some of these don't exist yet, and the list will change as I go. I try to keep this table in step with the repo.

## Coordinates and calibration

Everything is in meters, with the origin at the **center of the net on the court surface**:

- `x` runs across the court, and the singles sidelines are at about ±4.115 m.
- `y` runs along the court, and the baselines are at about ±11.885 m.
- The service line is 6.40 m from the net.

Each camera gets its own calibration, because each sees the court from a different spot. Both map into the same coordinate system, so a measurement means the same thing whichever camera made it.

There's one catch that shapes the whole design. A homography is only valid for points **on the court surface**. A ball in the air sits above that plane, so converting its image position directly gives a wrong court position. The system only converts the bounce point, the moment the ball touches the ground, and never a ball in flight.

When calibrating, don't judge accuracy from the points used to build the matrix, since a fit to those will look perfect. Keep a few landmarks aside, measure the error on them, and use that as the error margin for line calls.

## Getting started

Clone the repo and set up a virtual environment:

```bash
git clone <repository-url>
cd <repository-folder>
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

Then install the dependencies, with `requirements.txt` if there is one:

```bash
python -m pip install -r requirements.txt
```

or just the basics:

```bash
python -m pip install opencv-python numpy
```

Then set up the cameras. Connect each one, make sure the OS sees it, and test it on its own before running the full app. Note the real frame size and frame rate you get, and point `camera_left.py` and `camera_right.py` at the right devices.

## Running it

```bash
python main.py
```

`main.py` runs in stages, so you can check each part before turning on the next. Change `STAGE` at the top of the file:

| Stage | Adds |
|---|---|
| 1 | Streams both cameras and prints the frame rate |
| 2 | Shows both feeds |
| 3 | Preprocessing, ball detection, and independent tracking |
| 4 | Court calibration and the ball's position in meters |
| 5 | Bounce detection and line calls (printed only) |
| 6 | Scoring and event logging |
| 7 | The scoreboard window |

If something looks off, drop back a stage and look at what that stage is producing.

## Testing

Test each piece on its own before trusting it in a match.

- **Cameras:** both give steady frames at the rate you expect.
- **Detector:** run it on recorded frames and look at the false positives, especially court lines, shoes, and bright clothing.
- **Tracker:** the track holds through a short gap and doesn't jump to a different bright object.
- **Calibration:** convert known landmarks and measure the error in meters, on points that weren't used to build the matrix.
- **Bounce:** recorded clips where you know where the ball landed.
- **Line calls:** points clearly inside, clearly outside, and right on each line, including near corners.
- **Scoring:** deuce, advantage, tiebreaks, changeovers, and the end of a set and a match.
- **Integration:** make sure one bounce can never award two points.

Until the system has been checked against real ground truth, treat its calls as predictions. Close calls should come back as UNCERTAIN and get logged for review.

## Known challenges

- With a mono camera, anything bright looks like a ball: court lines, reflections, white clothing.
- Getting the cameras to stream at all depends on drivers and the interface.
- Accuracy is limited by how well you can pick out court landmarks in the image, and it gets worse far from each camera.
- The ball's image position doesn't tell you where it touched the ground unless it's actually on the ground.
- High frame rates mean a lot of data and a lot of processing for a Pi.
- Bounces and net contacts are short and often partly hidden.
- Both cameras have to use the same court coordinates before their results can be compared.

## A note on use

This is an experimental hobby project, not a certified officiating system. Use it as an aid for practice and casual play, and agree with the other players beforehand what happens with a call the system marks as uncertain.

## Contributing

Keep each module to one job, write down any config changes, and test against recorded frames or clips before taking a change onto the court.

## License

No license picked yet. Add one before sharing the project publicly.