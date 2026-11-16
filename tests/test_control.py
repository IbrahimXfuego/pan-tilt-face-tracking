from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'python'))
from control import Settings, Tracker, command

class ControlTests(unittest.TestCase):
    def test_center(self):
        t = Tracker()
        self.assertEqual(t.update(320, 240, 640, 480), (90, 90))
    def test_v3_first_step(self):
        t = Tracker()
        self.assertEqual(t.update(640, 480, 640, 480), (98, 96))
    def test_bounds_and_clipping(self):
        t = Tracker()
        for _ in range(300): t.update(2000, -50, 640, 480)
        self.assertAlmostEqual(t.pan, 135)
        self.assertAlmostEqual(t.tilt, 55)
    def test_axis_reversal(self):
        t = Tracker(Settings(smoothing=1, invert_pan=True, invert_tilt=True))
        self.assertEqual(t.update(0, 0, 640, 480), (135, 125))
    def test_reset_and_protocol(self):
        t = Tracker(); t.update(0, 0, 640, 480)
        self.assertEqual(command(*t.center()), b'90,90\n')
        with self.assertRaises(ValueError): command(181, 90)
    def test_bad_configuration(self):
        with self.assertRaises(ValueError): Tracker(Settings(smoothing=0))
        with self.assertRaises(ValueError): Tracker(Settings(pan_range=100))
        with self.assertRaises(ValueError): Tracker().update(0, 0, 0, 480)

if __name__ == '__main__': unittest.main()
