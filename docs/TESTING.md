# Checks and operation

## Python checks

From the repository root:

```sh
python -m unittest discover -s tests -p "test_*.py" -v
```

Checks cover the configurable launcher's V3-style mapping, smoothing, travel boundaries, axis inversion, centring, serial formatting and invalid settings.

## Serial movement check

Review the movement limits, edit the port in `python/serial_test.py`, upload the Arduino sketch and run:

```sh
cd python
python serial_test.py
```

The script sends six positions with two-second intervals, ending at 90°,90°.

## Operation sequence

1. Verify the Arduino sketch and pin wiring.
2. Keep the laser off; check neutral servo positions and mechanical clearances.
3. Check camera detection with `track.py --preview`.
4. Start V3 or the launcher with the correct serial port.
5. Move a face across the image and check pan/tilt direction and limits.
6. Remove the face and observe V3's hold behaviour.
7. Quit normally and check the requested centre position.
8. Compare the earlier versions when studying dead zones, proportional steps, smoothing and return-to-centre behaviour.
