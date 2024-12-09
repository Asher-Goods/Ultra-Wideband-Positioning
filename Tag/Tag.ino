// Include Libraries
#include <Wire.h>                // Include wire/I2C library
#define UWB_BAUD 115200
#define RXD2 16
#define TXD2 17

HardwareSerial uwbSerial(2);
void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);         
  uwbSerial.begin(UWB_BAUD, SERIAL_8N1, RXD2, TXD2);

  Serial.println("Configuring Tag....");
  Serial.println("");

  // uwbSerial.println("AT+MODE=0");
  // delay(1000);
  // uwbSerial.println("AT+NETWORKID=5");
  // delay(1000);
  // uwbSerial.println("AT+ADDRESS=9");
  // delay(1000);
  // uwbSerial.println("AT+CPIN=00000000000000000000000000000001");
  // delay(1000);
  
  Serial.println("Starting....");
  Serial.println("");
  
}

void loop() {
  // put your main code here, to run repeatedly:
  // Check if data is available on the second serial port
  while (uwbSerial.available() > 0) {
    // Read the user input from the second serial port
    char userInput = uwbSerial.read();
    // Print the received character to the default serial port
    Serial.print(userInput);
  }
}
