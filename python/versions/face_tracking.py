import cv2
import serial
import time

# -----------------------------
# Arduino Serial
# -----------------------------
arduino = serial.Serial("COM9", 115200)
time.sleep(2)

# -----------------------------
# Servo Initial Angles
# -----------------------------
pan = 90
tilt = 90

# -----------------------------
# Face Detector
# -----------------------------
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

cap = cv2.VideoCapture(0)

dead_zone = 25

while True:

    ret, frame = cap.read()

    if not ret:
        break

    frame = cv2.flip(frame, 1)

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.2,
        minNeighbors=5,
        minSize=(60, 60)
    )

    h, w = frame.shape[:2]

    # Screen Center
    cv2.circle(frame, (w//2, h//2), 6, (255,0,0), -1)

    for (x, y, fw, fh) in faces:

        cx = x + fw//2
        cy = y + fh//2

        error_x = cx - w//2
        error_y = cy - h//2

        # Draw Face
        cv2.rectangle(frame,(x,y),(x+fw,y+fh),(0,255,0),2)

        cv2.circle(frame,(cx,cy),5,(0,0,255),-1)

        cv2.line(frame,(w//2,h//2),(cx,cy),(0,255,255),2)

        # -----------------------------
        # Pan Control
        # -----------------------------
        if error_x > dead_zone:
            pan += 1

        elif error_x < -dead_zone:
            pan -= 1

        # -----------------------------
        # Tilt Control
        # -----------------------------
        if error_y > dead_zone:
            tilt += 1

        elif error_y < -dead_zone:
            tilt -= 1

        # Servo Limits
        pan = max(0, min(180, pan))
        tilt = max(0, min(180, tilt))

        # Send to Arduino
        message = f"{pan},{tilt}\n"
        arduino.write(message.encode())

        # Display
        cv2.putText(frame,
                    f"Pan:{pan}",
                    (10,30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0,255,0),
                    2)

        cv2.putText(frame,
                    f"Tilt:{tilt}",
                    (10,60),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0,255,0),
                    2)

        cv2.putText(frame,
                    f"ErrorX:{error_x}",
                    (10,90),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255,255,255),
                    2)

        cv2.putText(frame,
                    f"ErrorY:{error_y}",
                    (10,120),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255,255,255),
                    2)

        # Track only the first detected face
        break

    cv2.imshow("AI Face Tracking Turret", frame)

    key = cv2.waitKey(1) & 0xFF

    if key == ord('q') or key == 27:
        break

cap.release()
arduino.close()
cv2.destroyAllWindows()