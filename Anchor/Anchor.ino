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

#define MODE 1
#define NETWORKID 5
// change depending on which anchor you are programming
#define ADDRESS 10
#define CPIN "00000000000000000000000000000001"

HardwareSerial uwbSerial(2);

// Wi-Fi credentials
const char *ssid = "Asher-PC";       // Replace with your Wi-Fi SSID
const char *password = "location"; // Replace with your Wi-Fi password

// UDP configuration
WiFiUDP udp;
const char *host = "192.168.137.1"; // Replace with your server's IP
const uint16_t port = 50000;

// ANCHOR send command
String ANCHOR_SendMSG_cmd = "AT+ANCHOR_SEND=9,4,TEST\r\n";

// Variables for timer
unsigned long sendInterval = 500;
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
  // Configure UWB module
  configureUWBDevice();
  // configure Wifi
  configureWifi();
  // Clear UART buffer
  uwbSerial.flush(); 
  delay(10);

}

void configureWifi() {
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
  
  // Add the distance and device address
  jsonDoc["device_address"] = String(ADDRESS); // Send UWB device address
  jsonDoc["distance"] = distance;

  // Serialize JSON to a string
  char buffer[256];
  size_t jsonLength = serializeJson(jsonDoc, buffer);

  // Send JSON data via UDP
  udp.beginPacket(host, port);
  udp.write((uint8_t *)buffer, jsonLength);
  udp.endPacket();

  Serial.println("Distance sent over UDP: " + distance);
  Serial.println("Device Address: " + String(ADDRESS));
}

// Function to configure the UWB device
void configureUWBDevice() {
  Serial.println("Configuring UWB Device...");
  
  // Configure Mode
  String modeCommand = "AT+MODE=" + String(MODE) + "\r\n";
  sendATCommand(modeCommand, "MODE");

  // Configure Network ID
  String networkIDCommand = "AT+NETWORKID=" + String(NETWORKID) + "\r\n";
  sendATCommand(networkIDCommand, "NETWORK ID");

  // Configure Address
  String addressCommand = "AT+ADDRESS=" + String(ADDRESS) + "\r\n";
  sendATCommand(addressCommand, "ADDRESS");

  // Configure CPIN
  String cpinCommand = "AT+CPIN=" + String(CPIN) + "\r\n";
  sendATCommand(cpinCommand, "CPIN");

  Serial.println("UWB Device configuration completed.");
}

// Helper function to send AT commands and verify response
void sendATCommand(String command, String parameterName) {
  // Send the command
  uwbSerial.print(command);
  Serial.print("Sending command to configure ");
  Serial.print(parameterName);
  Serial.print(": ");
  Serial.println(command);

  // Wait for response
  delay(300);
  if (uwbSerial.available()) {
    String response = uwbSerial.readString();
    Serial.print("Response for ");
    Serial.print(parameterName);
    Serial.print(": ");
    Serial.println(response);

    // Check if the response contains the expected acknowledgment
    if (response.indexOf("+OK") != -1) {
      Serial.print(parameterName);
      Serial.println(" configured successfully.");
    } else {
      Serial.print("Error configuring ");
      Serial.println(parameterName);
    }
  } else {
    Serial.print("No response received for ");
    Serial.println(parameterName);
  }
}

void checkForUDPMessage() {
  char incomingPacket[256]; // Buffer for incoming packets
  int packetSize = udp.parsePacket();

  if (packetSize > 0) {
    // Read the incoming packet
    int len = udp.read(incomingPacket, sizeof(incomingPacket) - 1);
    if (len > 0) {
      incomingPacket[len] = '\0'; // Null-terminate the string
    }

    Serial.print("Received UDP message: ");
    Serial.println(incomingPacket);

    // Parse the incoming JSON
    StaticJsonDocument<200> jsonDoc;
    DeserializationError error = deserializeJson(jsonDoc, incomingPacket);

    if (error) {
      Serial.print("Failed to parse JSON: ");
      Serial.println(error.c_str());
      return;
    }

    // Check if polling interval is included in the JSON
    if (jsonDoc.containsKey("polling_period")) {
      unsigned long newInterval = jsonDoc["polling_period"];
      if (newInterval >= 10 && newInterval <= 60000) { // Validate interval range
        sendInterval = newInterval;
        Serial.print("Updated polling interval to: ");
        Serial.println(sendInterval);
      } else {
        Serial.println("Invalid send_interval value received.");
      }
    } else {
      Serial.println("send_interval key not found in received JSON.");
    }
  }
}

void loop() {
  // Timer-based message sending
  unsigned long currentTime = millis();
  if (currentTime - previousTime >= sendInterval) {
    sendMsg();
    previousTime = currentTime;
  }
  checkSerial();
  // check for incoming polling period updates
  checkForUDPMessage();
}
