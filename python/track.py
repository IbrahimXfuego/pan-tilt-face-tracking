"""Configurable launcher based on the supplied V3 face-to-angle mapping."""
import argparse
import time
from control import Settings, Tracker, command

def arguments():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--port', help='Arduino serial port, e.g. COM9 or /dev/ttyACM0')
    p.add_argument('--camera', type=int, default=0)
    p.add_argument('--baud', type=int, default=115200)
    p.add_argument('--width', type=int, default=640)
    p.add_argument('--height', type=int, default=480)
    p.add_argument('--smoothing', type=float, default=0.18)
    p.add_argument('--send-hz', type=float, default=50, help='Maximum command rate, not a guaranteed camera rate')
    p.add_argument('--invert-pan', action='store_true')
    p.add_argument('--invert-tilt', action='store_true')
    p.add_argument('--no-mirror', action='store_true')
    p.add_argument('--preview', action='store_true', help='Show detections/angles without opening serial')
    p.add_argument('--list-ports', action='store_true')
    return p.parse_args()

def main():
    args = arguments()
    try:
        import cv2
        import serial
        from serial.tools import list_ports
    except ImportError as exc:
        raise SystemExit('Install dependencies: python -m pip install -r requirements.txt') from exc
    if args.list_ports:
        for port in list_ports.comports():
            print(f'{port.device}: {port.description}')
        return
    if not args.preview and not args.port:
        raise SystemExit('Use --port COM9 (your actual port), or --preview for camera-only mode.')
    if not 0 < args.send_hz <= 50 or args.width <= 0 or args.height <= 0:
        raise SystemExit('Use positive dimensions and a send rate above 0 and at most 50 Hz.')
    tracker = Tracker(Settings(smoothing=args.smoothing, invert_pan=args.invert_pan, invert_tilt=args.invert_tilt))
    detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    if detector.empty():
        raise SystemExit('OpenCV could not load its bundled face cascade.')
    board, cap = None, None
    try:
        if not args.preview:
            board = serial.Serial(args.port, args.baud, timeout=0.1, write_timeout=1)
            time.sleep(2)
            board.write(command(*tracker.center()))
        cap = cv2.VideoCapture(args.camera)
        if not cap.isOpened():
            raise RuntimeError('Cannot open webcam. Check camera index and close other camera applications.')
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, args.width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, args.height)
        previous = time.monotonic()
        last_send = previous
        last_angles = (90, 90)
        while True:
            ok, frame = cap.read()
            if not ok:
                raise RuntimeError('Camera frame could not be read.')
            if not args.no_mirror:
                frame = cv2.flip(frame, 1)
            h, w = frame.shape[:2]
            center = (w // 2, h // 2)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = detector.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=6, minSize=(70, 70))
            cv2.circle(frame, center, 5, (255, 0, 0), -1)
            status = 'NO FACE | holding position'
            if len(faces):
                x, y, fw, fh = max(faces, key=lambda f: f[2] * f[3])
                cx, cy = int(x + fw // 2), int(y + fh // 2)
                angles = tracker.update(cx, cy, w, h)
                cv2.rectangle(frame, (x, y), (x + fw, y + fh), (0, 255, 0), 2)
                cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)
                cv2.line(frame, center, (cx, cy), (0, 255, 255), 2)
                now = time.monotonic()
                if board and now - last_send >= 1 / args.send_hz:
                    if angles != last_angles:
                        board.write(command(*angles))
                        last_angles = angles
                    last_send = now
                status = 'TRACKING' if board else 'PREVIEW | no motor commands'
            now = time.monotonic()
            fps = 1 / max(now - previous, 1e-6)
            previous = now
            for i, text in enumerate((f'PAN: {tracker.pan:.0f}', f'TILT: {tracker.tilt:.0f}', status)):
                cv2.putText(frame, text, (10, 30 + 30 * i), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.putText(frame, f'FPS: {fps:.1f} | C: center | Q / Esc: quit', (10, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
            cv2.imshow('Pan-Tilt Face Tracking', frame)
            key = cv2.waitKey(1) & 0xff
            if key in (ord('q'), 27):
                break
            if key == ord('c'):
                angles = tracker.center()
                if board:
                    board.write(command(*angles))
                last_angles = angles
                last_send = time.monotonic()
    except (RuntimeError, OSError, serial.SerialException) as exc:
        raise SystemExit(str(exc)) from exc
    finally:
        if board:
            try:
                board.write(command(*tracker.center()))
                board.flush()
            except (OSError, serial.SerialException):
                pass
            board.close()
        if cap:
            cap.release()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
