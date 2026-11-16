
import serial
import time

# Change this if your COM port changes
arduino = serial.Serial("COM9", 115200)

time.sleep(2)  # Wait for Arduino to reset

positions = [
    (90, 90),
    (120, 90),
    (60, 90),
    (90, 120),
    (90, 60),
    (90, 90)
]

for pan, tilt in positions:
    message = f"{pan},{tilt}\n"
    print("Sending:", message.strip())

    arduino.write(message.encode())

    time.sleep(2)

arduino.close()

print("Done!")