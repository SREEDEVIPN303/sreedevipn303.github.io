# LifeSignal – rescue robot firmware (sample)

Reference Arduino sketch for a low-cost rescue robot that drives forward, avoids obstacles with an ultrasonic sensor and stops with a buzzer alert when a PIR sensor detects sustained human presence. It reports events over serial as JSON, so a gateway (for example a Django endpoint like `sensorhub`) can ingest them.

**Status:** sample code for portfolio purposes; not tested on physical hardware.

| Part | Pins |
|---|---|
| HC-SR04 | TRIG 9, ECHO 10 |
| HC-SR501 PIR | OUT 2 |
| Buzzer | 8 |
| L298N left motor | ENA 5, IN1 4, IN2 3 |
| L298N right motor | ENB 6, IN3 12, IN4 11 |

Open `lifesignal.ino` in the Arduino IDE, select an Uno/Nano, and upload.
