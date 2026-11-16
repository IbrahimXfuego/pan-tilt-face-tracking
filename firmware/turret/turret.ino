#include <Servo.h>

// Create servo objects
Servo pan;
Servo tilt;

// Initial servo positions
int panAngle = 90;
int tiltAngle = 90;

void setup()
{
    // Start serial communication
    Serial.begin(115200);

    // Attach servos
    pan.attach(9);
    tilt.attach(10);

    // Set initial positions
    pan.write(panAngle);
    tilt.write(tiltAngle);
}

void loop()
{
    if (Serial.available())
    {
        // Read angles sent by Python
        String data = Serial.readStringUntil('\n');

        // Find comma separator
        int comma = data.indexOf(',');

        if (comma > 0)
        {
            // Extract pan and tilt angles
            panAngle = data.substring(0, comma).toInt();
            tiltAngle = data.substring(comma + 1).toInt();

            // Limit servo angles
            panAngle = constrain(panAngle, 0, 180);
            tiltAngle = constrain(tiltAngle, 0, 180);

            // Move servos
            pan.write(panAngle);
            tilt.write(tiltAngle);
        }
    }
}
