import cv2
import serial
import time
import numpy as np

# ==========================
# SETTINGS
# ==========================
COM_PORT = "COM9"
BAUD = 115200

CAM_WIDTH = 640
CAM_HEIGHT = 480

PAN_CENTER = 90
PAN_RANGE = 45      # Servo moves from 45° to 135°

TILT_CENTER = 90
TILT_RANGE = 35     # Servo moves from 55° to 125°

PAN_MIN = PAN_CENTER - PAN_RANGE
PAN_MAX = PAN_CENTER + PAN_RANGE

TILT_MIN = TILT_CENTER - TILT_RANGE
TILT_MAX = TILT_CENTER + TILT_RANGE

SMOOTHING = 0.18      # 0.1 = smoother, 0.3 = faster
UPDATE_TIME = 0.02    # 50Hz

# ==========================
# SERIAL
# ==========================
arduino = serial.Serial(COM_PORT, BAUD)
time.sleep(2)

# ==========================
# CAMERA
# ==========================
cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAM_WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_HEIGHT)

# ==========================
# FACE DETECTOR
# ==========================
face = cv2.CascadeClassifier(
    cv2.data.haarcascades +
    "haarcascade_frontalface_default.xml"
)

# ==========================
# INITIAL SERVO POSITION
# ==========================
pan = 90.0
tilt = 90.0

last_pan = -1
last_tilt = -1

last_send = time.time()

prev = time.time()

while True:

    ret, frame = cap.read()

    if not ret:
        break

    frame = cv2.flip(frame,1)

    gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)

    faces = face.detectMultiScale(
        gray,
        scaleFactor=1.2,
        minNeighbors=6,
        minSize=(70,70)
    )

    h,w = frame.shape[:2]

    center_x = w//2
    center_y = h//2

    cv2.circle(frame,(center_x,center_y),5,(255,0,0),-1)

    if len(faces):

        faces = sorted(
            faces,
            key=lambda f:f[2]*f[3],
            reverse=True
        )

        x,y,fw,fh = faces[0]

        cx = x + fw//2
        cy = y + fh//2

        cv2.rectangle(
            frame,
            (x,y),
            (x+fw,y+fh),
            (0,255,0),
            2
        )

        cv2.circle(
            frame,
            (cx,cy),
            5,
            (0,0,255),
            -1
        )

        cv2.line(
            frame,
            (center_x,center_y),
            (cx,cy),
            (0,255,255),
            2
        )

        # ----------------------------------
        # MAP FACE POSITION TO SERVO ANGLES
        # ----------------------------------

        target_pan = np.interp(
            cx,
            [0,w],
            [PAN_MIN,PAN_MAX]
        )

        # Tilt reversed intentionally
        target_tilt = np.interp(
            cy,
            [0,h],
            [TILT_MIN,TILT_MAX]
        )

        # ----------------------------------
        # SMOOTH MOVEMENT
        # ----------------------------------

        pan += (target_pan-pan)*SMOOTHING
        tilt += (target_tilt-tilt)*SMOOTHING

        pan = np.clip(
            pan,
            PAN_MIN,
            PAN_MAX
        )

        tilt = np.clip(
            tilt,
            TILT_MIN,
            TILT_MAX
        )
                # ----------------------------------
        # SEND TO ARDUINO (50 Hz)
        # ----------------------------------

        now = time.time()

        if now - last_send >= UPDATE_TIME:

            send_pan = int(round(pan))
            send_tilt = int(round(tilt))

            # Only send if something changed
            if send_pan != last_pan or send_tilt != last_tilt:

                arduino.write(
                    f"{send_pan},{send_tilt}\n".encode()
                )

                last_pan = send_pan
                last_tilt = send_tilt

            last_send = now

        # ----------------------------------
        # DISPLAY
        # ----------------------------------

        cv2.putText(
            frame,
            f"PAN : {int(pan)}",
            (10,30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0,255,0),
            2
        )

        cv2.putText(
            frame,
            f"TILT: {int(tilt)}",
            (10,60),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0,255,0),
            2
        )

        cv2.putText(
            frame,
            "TRACKING",
            (10,90),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0,255,0),
            2

        )

    else:

        cv2.putText(
            frame,
            "NO FACE",
            (10,30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0,0,255),
            2
        )

    # ----------------------------------
    # FPS
    # ----------------------------------

    current = time.time()

    fps = 1/(current-prev)

    prev = current

    cv2.putText(
        frame,
        f"FPS: {int(fps)}",
        (10,h-20),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255,255,0),
        2
    )

    cv2.imshow(
        "AI Face Tracking Turret V3",
        frame
    )

    key = cv2.waitKey(1) & 0xFF

    if key == ord("q") or key == 27:
        break

# ----------------------------------
# CLEANUP
# ----------------------------------

arduino.write(b"90,90\n")

time.sleep(0.3)

arduino.close()

cap.release()

cv2.destroyAllWindows()