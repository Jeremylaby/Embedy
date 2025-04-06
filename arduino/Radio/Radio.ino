#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>

#define UPPER_MID 520
#define LOWER_MID 500

const uint64_t pipeOut = 0xE9E8F0F0E1LL;  // Adres komunikacyjny (musi być zgodny z odbiornikiem)
RF24 radio(7, 8); // CE, CSN piny

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
  radio.setAutoAck(false);
  radio.openWritingPipe(pipeOut);      // Adres odbiornika
  radio.stopListening();               // Tryb nadawania

  ResetData();

  Serial.println("Nadajnik uruchomiony!");
}

// Mapowanie sygnału analogowego (z joysticka) do zakresu 0-255
int parseValue(int val) {
  val = constrain(val, 0, 1023);

  if (val >= LOWER_MID && val <= UPPER_MID) {
    return 127; // Martwa strefa (środek)
  } else if (val < LOWER_MID) {
    return map(val, 0, LOWER_MID, 0, 127); // Ruch wsteczny
  } else { // val > UPPER_MID
    return map(val, UPPER_MID, 1023, 128, 255); // Ruch do przodu
  }
}

void loop() {
  // Odczyt z joysticka
  data.motor1 = parseValue(analogRead(A0)); // Joystick 1
  data.motor2 = parseValue(analogRead(A2)); // Joystick 2

  // Debug - Serial monitor
  Serial.print("motor1 = ");
  Serial.print(data.motor1);
  Serial.print(" ; motor2 = ");
  Serial.println(data.motor2);

  // Wysyłanie danych
  bool success = radio.write(&data, sizeof(MotorSignal));

  if (success) {
    Serial.println("Wysłano dane.");
  } else {
    Serial.println("Błąd wysyłania!");
  }

  // (Opcjonalnie) sprawdzenie połączenia z nRF
  if (!radio.isChipConnected()) {
    Serial.println("nRF24L01 nie wykryty!");
  }

  delay(100); // Odstęp między wysyłaniem
}
