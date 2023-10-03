#include <ArduinoJson.h>

// Define the pin numbers for the LEDs
const int blueLedPin = 11;
const int greenLedPin = 12;
const int orangeLedPin = 13;

// Variables to store the state of each LED
bool blueLedState = false;
bool greenLedState = false;
bool orangeLedState = false;

void setup() {
  // Initialize the LED pins as outputs
  pinMode(blueLedPin, OUTPUT);
  pinMode(greenLedPin, OUTPUT);
  pinMode(orangeLedPin, OUTPUT);

  // Initialize the serial communication
  Serial.begin(9600);

  // Initially turn off all LEDs
  digitalWrite(blueLedPin, LOW);
  digitalWrite(greenLedPin, LOW);
  digitalWrite(orangeLedPin, LOW);
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    
    // Parse the JSON command
    StaticJsonDocument<200> doc;
    DeserializationError error = deserializeJson(doc, command);

    if (!error) {
      // Check the state of each LED and update accordingly
      if (strcmp(doc["color_channels"]["orange"], "on") == 0) {
        digitalWrite(orangeLedPin, HIGH); // Turn on the orange LED
      } else {
        digitalWrite(orangeLedPin, LOW);  // Turn off the orange LED
      }
      
      if (strcmp(doc["color_channels"]["green"], "on") == 0) {
        digitalWrite(greenLedPin, HIGH);  // Turn on the green LED
      } else {
        digitalWrite(greenLedPin, LOW);   // Turn off the green LED
      }
      
      if (strcmp(doc["color_channels"]["blue"], "on") == 0) {
        digitalWrite(blueLedPin, HIGH);   // Turn on the blue LED
      } else {
        digitalWrite(blueLedPin, LOW);    // Turn off the blue LED
      }
    }
  }
}
