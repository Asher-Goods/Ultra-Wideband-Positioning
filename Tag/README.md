# ESP32 UWB Tag Code Summary

## Overview
This code sets up an **ESP32-based UWB (Ultra-Wideband) tag device**. The tag communicates over UART to interface with a UWB module, and it relays received serial data for debugging purposes via the default serial port.

---

## Key Functions & Workflow

### 1. Initialization (`setup()`)
- **Serial Debugging**: Initializes serial communication at `115200` for monitoring/debugging.
- **UWB Serial Setup**: Establishes UART2 communication with the UWB device using the specified RXD2/TXD2 pins and baud rate.
- Prints configuration messages to indicate UWB tag setup and initialization status.

---

## Main Components

### 1. **UWB Serial Communication**
- Established via `HardwareSerial` with the UWB module.
- Configured using the `SERIAL_8N1`, `RXD2`, and `TXD2` pins at a baud rate of `115200`.

### 2. **Debugging & Serial Monitoring**
- The program continuously monitors data from the UWB module (via UART2).
- Any received data is relayed to the default serial port for debugging purposes.

---

## Workflow in `loop()`
1. **Check for Incoming Data**:
   - Continuously checks if there is data available on the `uwbSerial`.
2. **Relay Received Data**:
   - Reads characters from the UWB communication interface.
   - Prints these characters to the default serial monitor (`Serial.print`) for observation.

---

## Configurable Parameters
1. `UWB_BAUD`: Defines baud rate for UWB communication (`115200`).
2. `RXD2`, `TXD2`: Define the GPIO pins used for UWB communication (default `16`, `17`).

---

## Dependencies
The following libraries are used:
- **Wire.h**: Includes I2C communication support if needed later.
- **HardwareSerial**: Used for UART communication with the UWB module.

---

## Example Debugging Output
When connected and running, any received UWB data will be visible in the default Serial Monitor. For example:
```plaintext
Received Data: A1B2C3D4
