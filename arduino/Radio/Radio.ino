#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>

#define UPPER_MID 520
#define LOWER_MID 500

const uint64_t pipeOut = 0xF0F0F0F0E1LL;  // Adres komunikacyjny (musi być zgodny z odbiornikiem)
RF24 radio(9, 10); // CE, CSN piny

struct MotorSignal {
  byte motor1;
  byte motor2;
};

MotorSignal data;

void ResetData() {
  data.motor1 = 127;
  data.motor2 = 127;
}

void setup() {
  Serial.begin(9600);
  
  if (!radio.begin()) {
    Serial.println("Błąd inicjalizacji nRF24L01!");
    while (1); // Zatrzymaj program
  }

         
  radio.setDataRate(RF24_250KBPS); 
  radio.openWritingPipe(pipeOut);
  radio.setPALevel(RF24_PA_HIGH);
  radio.setChannel(100);
  radio.setAutoAck(false);
  radio.powerUp();    
  ResetData();

  Serial.println("Nadajnik uruchomiony!");
}

// Mapowanie sygnału analogowego (z joysticka) do zakresu 0-255
int parseValue(int val) {
  val = constrain(val, 0, 1023);

  if (val >= LOWER_MID && val <= UPPER_MID) {
    return 127;
  } else if (val < LOWER_MID) {
    return map(val, 0, LOWER_MID, 0, 127); // Ruch wsteczny
  } else {
    return map(val, UPPER_MID, 1023, 128, 255); // Ruch do przodu
  }
}

void loop() {

  data.motor1 = parseValue(analogRead(A0)); // Joystick 1
  data.motor2 = parseValue(analogRead(A2)); // Joystick 2

  // Debug - Serial monitor
  Serial.print("motor1 = ");
  Serial.print(data.motor1);
  Serial.print(" ; motor2 = ");
  Serial.println(data.motor2);

  bool success = radio.write(&data, sizeof(data));

  if (success) {
    Serial.println("Wysłano dane.");
  } else {
    Serial.println("Błąd wysyłania!");
  }


  delay(50);
}
