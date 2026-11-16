import cv2
import serial
import time

# ==========================
# SERIAL COMMUNICATION
# ==========================
arduino = serial.Serial("COM9", 115200)
time.sleep(2)

# ==========================
# FACE DETECTOR
# ==========================
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Could not open webcam.")
    exit()

# ==========================
# CAMERA SETTINGS
# ==========================
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# ==========================
# SERVO SETTINGS
# ==========================
pan = 90.0
tilt = 90.0

PAN_MIN = 0
PAN_MAX = 180

TILT_MIN = 0
TILT_MAX = 180

# ==========================
# CONTROL PARAMETERS
# ==========================
Kp_x = 0.025
Kp_y = 0.06

DEAD_ZONE = 18

MAX_STEP = 4

# ==========================
# SMOOTHING
# ==========================
alpha = 0.35

smooth_x = None
smooth_y = None

# ==========================
# FACE LOST TIMER
# ==========================
last_face_time = time.time()

RETURN_DELAY = 2.0

# ==========================
# FPS
# ==========================
prev = time.time()

while True:

    ret, frame = cap.read()

    if not ret:
        break

    frame = cv2.flip(frame, 1)

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.2,
        minNeighbors=6,
        minSize=(70,70)
    )

    h, w = frame.shape[:2]

    print(w, h)


    center_x = w // 2
    center_y = h // 2

    cv2.circle(frame,(center_x,center_y),6,(255,0,0),-1)

    face_found = False

    if len(faces) > 0:

        face_found = True

        last_face_time = time.time()

        # Track largest face
        faces = sorted(faces,
                       key=lambda f: f[2]*f[3],
                       reverse=True)

        x,y,fw,fh = faces[0]

        cx = x + fw//2
        cy = y + fh//2

        # -------------------
        # LOW PASS FILTER
        # -------------------
        if smooth_x is None:
            smooth_x = cx
            smooth_y = cy
        else:
            smooth_x = alpha*cx + (1-alpha)*smooth_x
            smooth_y = alpha*cy + (1-alpha)*smooth_y

        cx = int(smooth_x)
        cy = int(smooth_y)

        # -------------------
        # DRAWING
        # -------------------
        cv2.rectangle(frame,
                      (x,y),
                      (x+fw,y+fh),
                      (0,255,0),
                      2)

        cv2.circle(frame,
                   (cx,cy),
                   5,
                   (0,0,255),
                   -1)

        cv2.line(frame,
                 (center_x,center_y),
                 (cx,cy),
                 (0,255,255),
                 2)

        error_x = cx-center_x
        error_y = cy-center_y

        # -------------------
        # DEAD ZONE
        # -------------------
        if abs(error_x) < DEAD_ZONE:
            error_x = 0

        if abs(error_y) < DEAD_ZONE:
            error_y = 0

        # -------------------
        # PROPORTIONAL CONTROL
        # -------------------
        move_pan = Kp_x * error_x
        move_tilt = Kp_y * error_y
        # Limit movement speed
        if move_pan > MAX_STEP:
            move_pan = MAX_STEP
        if move_pan < -MAX_STEP:
            move_pan = -MAX_STEP

        if move_tilt > MAX_STEP:
            move_tilt = MAX_STEP
        if move_tilt < -MAX_STEP:
            move_tilt = -MAX_STEP
                    # -------------------
        # UPDATE SERVO ANGLES
        # -------------------

        # Reverse X direction if needed
        pan += move_pan

        # Reverse Y direction if needed
        tilt -= move_tilt

        # Servo limits
        pan = max(PAN_MIN, min(PAN_MAX, pan))
        tilt = max(TILT_MIN, min(TILT_MAX, tilt))

        # -------------------
        # SEND TO ARDUINO
        # -------------------
        message = f"{int(pan)},{int(tilt)}\n"
        arduino.write(message.encode())

        # -------------------
        # DISPLAY INFO
        # -------------------
        cv2.putText(frame,
                    f"PAN : {int(pan)}",
                    (10,30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0,255,0),
                    2)

        cv2.putText(frame,
                    f"TILT: {int(tilt)}",
                    (10,60),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0,255,0),
                    2)

        cv2.putText(frame,
                    f"Error X: {error_x}",
                    (10,90),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255,255,255),
                    2)

        cv2.putText(frame,
                    f"Error Y: {error_y}",
                    (10,120),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255,255,255),
                    2)

        cv2.putText(frame,
                    "TRACKING",
                    (10,150),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0,255,0),
                    2)

    else:

        # -------------------
        # RETURN TO CENTER
        # -------------------
        if time.time() - last_face_time > RETURN_DELAY:

            if pan < 90:
                pan += 0.5
            elif pan > 90:
                pan -= 0.5

            if tilt < 90:
                tilt += 0.5
            elif tilt > 90:
                tilt -= 0.5

            pan = max(PAN_MIN, min(PAN_MAX, pan))
            tilt = max(TILT_MIN, min(TILT_MAX, tilt))

            message = f"{int(pan)},{int(tilt)}\n"
            arduino.write(message.encode())

        cv2.putText(frame,
                    "SEARCHING...",
                    (10,30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0,0,255),
                    2)

    # -------------------
    # FPS
    # -------------------
    current = time.time()
    fps = 1/(current-prev)
    prev = current

    cv2.putText(frame,
                f"FPS: {int(fps)}",
                (10,h-20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255,255,0),
                2)

    cv2.imshow("AI Face Tracking Turret V2", frame)

    key = cv2.waitKey(1) & 0xFF

    if key == ord('q') or key == 27:
        break

# -------------------
# CLEANUP
# -------------------
arduino.write(b"90,90\n")
time.sleep(0.5)

arduino.close()
cap.release()
cv2.destroyAllWindows()