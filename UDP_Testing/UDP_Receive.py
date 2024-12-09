import socket
import json

# Server configuration
UDP_IP = "0.0.0.0"  # Listen on all available interfaces
UDP_PORT = 50000    # Match the port number used in the ESP32 code

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

print(f"Listening for UDP packets on {UDP_IP}:{UDP_PORT}...")

while True:
    # Receive data from the ESP32
    data, addr = sock.recvfrom(1024)  # Buffer size is 1024 bytes
    # print(f"Received packet from {addr}")

    try:
        # Decode and parse the JSON data
        json_data = json.loads(data.decode('utf-8'))
        # print("Received JSON data:")
        print(json.dumps(json_data, indent=4))
    except json.JSONDecodeError:
        print("Invalid JSON received:")
        print(data.decode('utf-8'))
