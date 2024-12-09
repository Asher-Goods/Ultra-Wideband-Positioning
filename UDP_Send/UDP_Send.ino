// Include Libraries
#include <Wire.h>
#include <WiFi.h>              // For Wi-Fi connection
#include <WiFiUDP.h>           // For UDP communication
#include <ArduinoJson.h>       // For JSON serialization

// Constants
#define UWB_BAUD 115200
#define RXD2 16
#define TXD2 17
#define RESET_PIN 4 // Define GPIO pin for Reset

HardwareSerial uwbSerial(2);

// Wi-Fi credentials
const char *ssid = "Pitt Police";       // Replace with your Wi-Fi SSID
const char *password = "Istanbulnumber1"; // Replace with your Wi-Fi password

// UDP configuration
WiFiUDP udp;
const char *host = "192.168.1.152"; // Replace with your server's IP
const uint16_t port = 50000;

// ANCHOR send command
String ANCHOR_SendMSG_cmd = "AT+ANCHOR_SEND=9,4,TEST\r\n";

// Variables for timer
const unsigned long sendInterval = 4000;
unsigned long previousTime = 0;

void setup() {
  // Serial for debugging
  Serial.begin(115200);

  // UART2 for UWB communication
  uwbSerial.begin(UWB_BAUD, SERIAL_8N1, RXD2, TXD2);

  // Configure Reset Pin
  pinMode(RESET_PIN, OUTPUT);
  digitalWrite(RESET_PIN, HIGH); // Set to HIGH initially (module operational)

  // Reset the UWB module
  resetUWBModule();

  // Connect to Wi-Fi
  Serial.print("Connecting to Wi-Fi...");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConnected to Wi-Fi.");
  Serial.print("ESP32 IP address: ");
  Serial.println(WiFi.localIP());

  // Begin UDP
  udp.begin(WiFi.localIP(), port);
  Serial.println("UDP client initialized.");

  // Test communication with UWB module
  Serial.println("Configuring Anchor...");
  delay(100);
  Serial.println("Starting...");
  delay(100);

  uwbSerial.flush(); // Clear UART buffer
  delay(10);

  uwbSerial.print("AT\r\n");
  delay(1000);

  if (uwbSerial.available()) {
    Serial.println("UWB Module is responding:");
    while (uwbSerial.available()) {
      char c = uwbSerial.read();
      Serial.print(c); // Print received character
    }
  } else {
    Serial.println("No response from UWB Module.");
  }
}

// Function to reset the UWB module
void resetUWBModule() {
  Serial.println("Resetting UWB Module...");
  digitalWrite(RESET_PIN, LOW); // Pull RESET_PIN low to trigger reset
  delay(100);                  // Hold reset for 100ms
  digitalWrite(RESET_PIN, HIGH); // Release reset (module operational)
  delay(1000);                 // Wait for the module to initialize
  Serial.println("Reset complete.");
}

// Function for sending Anchor Send command
void sendMsg() {
  Serial.println(ANCHOR_SendMSG_cmd);
  uwbSerial.print(ANCHOR_SendMSG_cmd);
}

// Function to parse incoming serial data
String getValue(String data, char separator, int index) {
  int found = 0;
  int strIndex[] = {0, -1};
  int maxIndex = data.length() - 1;

  for (int i = 0; i <= maxIndex && found <= index; i++) {
    if (data.charAt(i) == separator || i == maxIndex) {
      found++;
      strIndex[0] = strIndex[1] + 1;
      strIndex[1] = (i == maxIndex) ? i + 1 : i;
    }
  }
  return found > index ? data.substring(strIndex[0], strIndex[1]) : "";
}

// Function to check incoming serial data and send via UDP
void checkSerial() {
  while (uwbSerial.available() > 0) {
    // Get the incoming data string
    String inString = uwbSerial.readString();
    inString.remove(0, 3); // Remove +OK\n
    Serial.print("Received Data: ");
    Serial.println(inString);

    // Extract distance value
    String distance = getValue(inString, ',', 3); // Extract specific data
    Serial.print("Distance: ");
    Serial.println(distance);

    // Send the distance value via UDP
    sendDistanceUDP(distance);
  }
}

// Function to send distance over UDP
void sendDistanceUDP(String distance) {
  // Create JSON object
  StaticJsonDocument<200> jsonDoc;
  jsonDoc["distance"] = distance;

  // Serialize JSON to a string
  char buffer[256];
  size_t jsonLength = serializeJson(jsonDoc, buffer);

  // Send JSON data via UDP
  udp.beginPacket(host, port);
  udp.write((uint8_t *)buffer, jsonLength);
  udp.endPacket();

  Serial.println("Distance sent over UDP: " + distance);
}

void loop() {
  // Timer-based message sending
  unsigned long currentTime = millis();
  if (currentTime - previousTime >= sendInterval) {
    sendMsg();
    previousTime = currentTime;
  }
  checkSerial();
}
