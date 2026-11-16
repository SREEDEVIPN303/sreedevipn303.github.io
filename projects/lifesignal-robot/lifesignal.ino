/*
 * LifeSignal - reference firmware sketch for a low-cost search-and-rescue robot.
 * Sample project for portfolio purposes. Pin choices are examples; this sketch has
 * NOT been tested on physical hardware - verify wiring and thresholds before use.
 *
 * Sensors : HC-SR04 ultrasonic (obstacles), HC-SR501 PIR (human presence)
 * Drive   : L298N dual H-bridge + 2 DC motors
 * Output  : Buzzer + serial reports (to a PC / ESP32 gateway)
 */

const uint8_t PIN_TRIG = 9, PIN_ECHO = 10, PIN_PIR = 2, PIN_BUZZER = 8;
const uint8_t PIN_ENA = 5, PIN_IN1 = 4, PIN_IN2 = 3;     // left motor
const uint8_t PIN_ENB = 6, PIN_IN3 = 12, PIN_IN4 = 11;   // right motor

const int OBSTACLE_CM = 20;      // stop and turn below this distance
const int DRIVE_SPEED = 160;     // PWM 0-255
const unsigned long PIR_CONFIRM_MS = 1500;  // presence must persist to count as a detection

enum State { SEARCHING, AVOIDING, SURVIVOR_FOUND };
State state = SEARCHING;
unsigned long presenceSince = 0;

long readDistanceCm() {
  digitalWrite(PIN_TRIG, LOW);  delayMicroseconds(2);
  digitalWrite(PIN_TRIG, HIGH); delayMicroseconds(10);
  digitalWrite(PIN_TRIG, LOW);
  unsigned long us = pulseIn(PIN_ECHO, HIGH, 30000UL);   // 30 ms timeout
  return us == 0 ? 999 : (long)(us / 58);
}

void drive(int left, int right) {   // -255..255 per side
  digitalWrite(PIN_IN1, left  >= 0); digitalWrite(PIN_IN2, left  < 0);
  digitalWrite(PIN_IN3, right >= 0); digitalWrite(PIN_IN4, right < 0);
  analogWrite(PIN_ENA, abs(left));   analogWrite(PIN_ENB, abs(right));
}

void stopMotors() { drive(0, 0); }

void setup() {
  pinMode(PIN_TRIG, OUTPUT); pinMode(PIN_ECHO, INPUT);
  pinMode(PIN_PIR, INPUT);   pinMode(PIN_BUZZER, OUTPUT);
  for (uint8_t p : {PIN_ENA, PIN_IN1, PIN_IN2, PIN_ENB, PIN_IN3, PIN_IN4}) pinMode(p, OUTPUT);
  Serial.begin(9600);
  Serial.println(F("{\"event\":\"boot\"}"));
  delay(30000);  // PIR sensors need a warm-up period
}

void loop() {
  // 1) Human presence: require the PIR to stay HIGH to reject one-off noise
  if (digitalRead(PIN_PIR) == HIGH) {
    if (presenceSince == 0) presenceSince = millis();
    if (millis() - presenceSince > PIR_CONFIRM_MS && state != SURVIVOR_FOUND) {
      state = SURVIVOR_FOUND;
      stopMotors();
      digitalWrite(PIN_BUZZER, HIGH);
      Serial.println(F("{\"event\":\"survivor_detected\"}"));
    }
  } else {
    presenceSince = 0;
    if (state == SURVIVOR_FOUND) { digitalWrite(PIN_BUZZER, LOW); state = SEARCHING; }
  }
  if (state == SURVIVOR_FOUND) { delay(100); return; }

  // 2) Obstacle handling
  long cm = readDistanceCm();
  if (cm < OBSTACLE_CM) {
    state = AVOIDING;
    stopMotors(); delay(150);
    drive(-DRIVE_SPEED, -DRIVE_SPEED); delay(350);   // back up
    drive(DRIVE_SPEED, -DRIVE_SPEED);  delay(450);   // pivot right
    stopMotors();
    Serial.print(F("{\"event\":\"obstacle\",\"cm\":")); Serial.print(cm); Serial.println(F("}"));
    state = SEARCHING;
  } else {
    drive(DRIVE_SPEED, DRIVE_SPEED);
  }
  delay(60);
}
