# ESP32 UWB Anchor Code Summary

## Overview
This code sets up an **ESP32-based UWB (Ultra-Wideband) communication anchor device**. It communicates over UDP via Wi-Fi and interfaces with a UWB module for distance measurements. The system sends UWB data (distance information) over a UDP connection in JSON format to a server while also allowing for remote adjustments to the polling interval.

---

## Key Functions & Workflow

### 1. Initialization (`setup()`)
- **Serial Debugging**: Initializes serial communication for debugging purposes.
- **UART2 for UWB Communication**: Establishes a serial connection to communicate with the UWB device.
- **Reset UWB Device**: Resets the UWB module to ensure it's initialized correctly.
- **UWB Configuration**: Configures the UWB settings, such as operational mode, network ID, address, and CPIN.
- **Wi-Fi Setup**: Connects to a Wi-Fi network and initializes UDP for communication.

---

## Main Components

### 1. **UWB Module Configuration**
Sends AT commands to configure the UWB device with:
- **Mode**
- **Network ID**
- **Device Address**
- **CPIN**

### 2. **Wi-Fi & UDP Configuration**
- Connects to a Wi-Fi network (`ssid` and `password`) and sets up UDP communication to a server's IP address and port.

### 3. **Message Sending**
- Sends a test message (`ANCHOR_SendMSG_cmd`) every interval (`sendInterval`) over UART to the UWB device.
- Parses UWB data and sends extracted distance information via UDP using JSON.

### 4. **Data Parsing**
- Reads UWB distance data from UART, extracts it, and sends it over UDP.

### 5. **UDP Polling & Configuration Updates**
- Listens for incoming UDP messages to dynamically adjust the polling interval, which is validated and updated accordingly.

---

## Workflow in `loop()`
1. **Timer-Based Message Sending**: Sends the UWB anchor command at regular intervals.
2. **Serial Data Handling**: Reads data from UWB module and sends extracted distance information via UDP.
3. **UDP Message Polling**: Listens for incoming UDP messages that could dynamically change polling intervals.

---

## Communication

### 1. **UWB Data**
- The UWB module sends distance measurements.
- These values are extracted and sent to a server via UDP in JSON format.

### 2. **UDP Configuration**
- The server can send a JSON payload containing a new polling interval, which adjusts how frequently UWB data is sent.

---

## JSON Example Sent Over UDP
```json
{
  "device_address": "8",
  "distance": "123"
}
