# Wiring and power

## Signal and power table

| Wire | Connection |
| --- | --- |
| Pan MG996R orange/yellow signal | Arduino Uno D9 |
| Tilt MG996R orange/yellow signal | Arduino Uno D10 |
| Both servo red positive wires | Regulated external 5 V positive |
| Both servo brown/black negative wires | External 5 V negative/GND |
| Arduino GND | External supply GND |
| Arduino USB | Laptop for power and 115200-baud serial data |
| Webcam | Laptop/PC camera input |

Servo supply and Arduino share a **ground reference**, not a positive supply connection. Do not power the two MG996R servos from the Uno's 5V pin, and do not join the external 5 V positive to USB/Uno power unless using a deliberately designed power arrangement.

Choose a suitable regulated supply with enough peak current for both loaded servos; servo stall current is much higher than unloaded movement current. Use short, adequate power wiring and local decoupling when needed. Do not route servo current through a weak breadboard rail or thin USB-programming wiring.

The sketch attaches the servos to D9 and D10. Both are centred to 90° on reset, so keep the mechanism clear before power-up/upload. Firmware accepts 0–180°; the actual bracket's travel can be narrower. V3 uses pan 45–135° and tilt 55–125° by default.

The webcam provides image coordinates to Python; the Arduino does not run face detection. No laser-control pin or laser-switching circuit is implemented in the supplied code. Keep any laser switched off during face-tracking tests.
