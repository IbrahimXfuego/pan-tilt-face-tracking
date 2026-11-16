# Setup with Arduino IDE and Python

## Arduino

1. Connect the Uno through USB with servo power switched off.
2. Open `firmware/turret/turret.ino`.
3. Select **Tools → Board → Arduino Uno** and the Uno's serial port.
4. The sketch uses **Servo by Arduino**. Install it through Library Manager if needed.
5. Click Verify, then Upload.
6. Close Serial Monitor before running Python; one application should own the serial port.

The firmware uses D9 for pan, D10 for tilt and 115200 baud. A command like `90,120\n` sets the two angles. Its normal startup command is 90° on both axes.

## Windows Python environment

Install Python 3.10 or later. Open Command Prompt in the `python` folder:

```bat
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

List ports with the optional launcher:

```bat
.venv\Scripts\python.exe track.py --list-ports
```

Set `COM_PORT` in `face_tracking_v3.py` to that port, then run:

```bat
.venv\Scripts\python.exe face_tracking_v3.py
```

For the configurable launcher instead:

```bat
.venv\Scripts\python.exe track.py --port COM9
```

Replace COM9 with the actual port. The earlier versions and `serial_test.py` also contain a COM9 setting that can be edited.

## Linux/macOS

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python track.py --list-ports
.venv/bin/python track.py --port /dev/ttyACM0
```

Choose the actual device path. On Linux, the account may need serial-port permissions. Use the appropriate account/group configuration rather than running the tracker as root.

## Calibration sequence

1. Keep the laser off and the servo horns/mechanism clear.
2. Check the external 5 V supply, signal pins and common ground.
3. Establish neutral servo positions before securing the bracket.
4. Review the requested positions in `serial_test.py`. It includes tilt 60° and 120° and pan 60° and 120°. Reduce them if your bracket requires smaller travel.
5. Run `serial_test.py` after updating its port to check both axes.
6. With the configurable launcher, `--preview` checks camera detection without opening the motor serial connection.
7. Run V3 or the launcher, then confirm each direction with small movements.
8. The launcher offers `--invert-pan`, `--invert-tilt` and `--no-mirror`. In the original V3, edit the interpolation endpoints if the mounting requires the opposite direction.
9. Lower `SMOOTHING` for slower, smoother transitions; raise it cautiously for faster response.

## Webcam

Camera index 0 is used by default. Change `cv2.VideoCapture(0)` in the uploaded scripts if needed, or use `--camera 1` in the launcher. Close other applications that own the camera. The OpenCV GUI package is required for the preview windows; do not install only the headless variant.

## Common problems

| Symptom | Check |
| --- | --- |
| Cannot open COM port | Correct port; Serial Monitor closed; USB cable and driver |
| No webcam image | Camera index, privacy permissions and other camera applications |
| No face detections | Frontal face, lighting, distance and minimum detection size |
| Motion is reversed | Mirroring and axis mapping; bracket orientation |
| Jitter or resets | External supply current, common ground, mechanical load and smoothing |
| Servo reaches a mechanical stop | Reduce working limits; check neutral horn placement |
| Several faces cause switching | V3 chooses the largest detection each frame |

`UPDATE_TIME = 0.02` caps serial scheduling at 50 Hz; it does not make a slow camera or detector run at 50 FPS. Commands are skipped when rounded angles have not changed.
