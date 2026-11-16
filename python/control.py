"""Pure angle-mapping logic shared by the configurable tracker and its checks."""
from dataclasses import dataclass

@dataclass
class Settings:
    pan_center: float = 90
    tilt_center: float = 90
    pan_range: float = 45
    tilt_range: float = 35
    smoothing: float = 0.18
    invert_pan: bool = False
    invert_tilt: bool = False

    def validate(self):
        if not 0 < self.smoothing <= 1:
            raise ValueError('Smoothing must be greater than 0 and at most 1.')
        for center, travel in ((self.pan_center, self.pan_range), (self.tilt_center, self.tilt_range)):
            if travel <= 0 or center - travel < 0 or center + travel > 180:
                raise ValueError('Servo travel must remain within 0–180 degrees.')

class Tracker:
    def __init__(self, settings=None):
        self.settings = settings or Settings()
        self.settings.validate()
        self.pan = self.settings.pan_center
        self.tilt = self.settings.tilt_center

    def update(self, x, y, width, height):
        if width <= 0 or height <= 0:
            raise ValueError('Frame dimensions must be positive.')
        s = self.settings
        nx, ny = max(0, min(1, x / width)), max(0, min(1, y / height))
        if s.invert_pan:
            nx = 1 - nx
        if s.invert_tilt:
            ny = 1 - ny
        target_pan = s.pan_center + (2 * nx - 1) * s.pan_range
        target_tilt = s.tilt_center + (2 * ny - 1) * s.tilt_range
        self.pan += (target_pan - self.pan) * s.smoothing
        self.tilt += (target_tilt - self.tilt) * s.smoothing
        self.pan = max(s.pan_center - s.pan_range, min(s.pan_center + s.pan_range, self.pan))
        self.tilt = max(s.tilt_center - s.tilt_range, min(s.tilt_center + s.tilt_range, self.tilt))
        return round(self.pan), round(self.tilt)

    def center(self):
        self.pan = self.settings.pan_center
        self.tilt = self.settings.tilt_center
        return round(self.pan), round(self.tilt)

def command(pan, tilt):
    if not 0 <= pan <= 180 or not 0 <= tilt <= 180:
        raise ValueError('Command outside servo range.')
    return f'{int(pan)},{int(tilt)}\n'.encode('ascii')
