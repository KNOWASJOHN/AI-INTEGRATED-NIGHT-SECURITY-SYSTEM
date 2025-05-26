#include <LiquidCrystal_I2C.h>

const int SPin = 8;      // Digital pin connected to the PIR sensor
int RelayPin = 6;
int Buzzer = 13;
LiquidCrystal_I2C lcd(0x27, 16, 2);

void setup() {
  pinMode(SPin, INPUT);        // Set PIR sensor pin as input
  pinMode(Buzzer, OUTPUT);     // Set buzzer pin as output
  pinMode(RelayPin, OUTPUT);   // Set relay pin as output
  lcd.init();
  lcd.clear();         
  lcd.backlight();
  Serial.begin(9600);          // Initialize serial communication for debugging (optional)
  delay(20000);                // Wait for PIR sensor to stabilize
}

void loop() {
  int Senseval = digitalRead(SPin);
    if (Senseval == HIGH) {
      Serial.println("Motion detected!");
      Serial.println("Play Sound");
      String msg2 = Serial.readString();
      if(msg2=="person"){
        digitalWrite(RelayPin, LOW);   // Activate relay

        for (int i = 1; i<=5; i++)
          {
          digitalWrite(Buzzer, HIGH);
          delay(500);
          digitalWrite(Buzzer, LOW);
          delay(500);
          }
      delay(3000);
      }
      }
      
  else {
    Serial.println("No motion detected.");
    digitalWrite(RelayPin, HIGH);  // Deactivate relay
    digitalWrite(Buzzer, LOW);     // Turn off buzzer
    delay(500);
  }
}
