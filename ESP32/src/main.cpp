#include <Arduino.h>
#include <ESP32Servo.h>

Servo myservo;
const int servoPin = 13;

void setup() {
  myservo.attach(servoPin);
  myservo.write(0);
}
  

void loop() {
}

