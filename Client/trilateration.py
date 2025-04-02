import socket
import json
import math

# Default anchor positions (x, y, z) in centimeters
ANCHOR_1_POSITION = (0, 0, 90)
ANCHOR_2_POSITION = (660, 0, 90)
ANCHOR_3_POSITION = (250, 600, 90)

# Server configuration
SERVER_IP = "0.0.0.0"  # Listen on all available interfaces
SERVER_PORT = 50000    # Port number

# Anchor addresses (example IPs and ports)
ANCHOR_IPS = [
    ("192.168.1.170", 50000),
    ("192.168.1.171", 50000),
    ("192.168.1.173", 50000)
]

# Create a UDP socket
socket_connection = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
socket_connection.bind((SERVER_IP, SERVER_PORT))

print(f"Listening for UDP packets on {SERVER_IP}:{SERVER_PORT}...")

# Variables to store the latest distances
distance_from_anchor_1 = None
distance_from_anchor_2 = None
distance_from_anchor_3 = None
latest_tag_position = None  # Variable to store the latest calculated tag position

def calculate_position(anchor1_pos, anchor2_pos, anchor3_pos, distance1, distance2, distance3):
    """
    Calculate the position of the tag using trilateration from three anchors.
    
    Args:
        anchor1_pos: Position of the first anchor (x, y, z)
        anchor2_pos: Position of the second anchor (x, y, z)
        anchor3_pos: Position of the third anchor (x, y, z)
        distance1: Distance from first anchor in cm
        distance2: Distance from second anchor in cm
        distance3: Distance from third anchor in cm
        
    Returns:
        Tuple (x, y, z) with position coordinates
    """
    # Trilateration algorithm
    A = 2*anchor2_pos[0] - 2*anchor1_pos[0]
    B = 2*anchor2_pos[1] - 2*anchor1_pos[1]
    C = distance1**2 - distance2**2 - anchor1_pos[0]**2 + anchor2_pos[0]**2 - anchor1_pos[1]**2 + anchor2_pos[1]**2
    D = 2*anchor3_pos[0] - 2*anchor2_pos[0]
    E = 2*anchor3_pos[1] - 2*anchor2_pos[1]
    F = distance2**2 - distance3**2 - anchor2_pos[0]**2 + anchor3_pos[0]**2 - anchor2_pos[1]**2 + anchor3_pos[1]**2
    
    x = (C*E - F*B) / (E*A - B*D)
    y = (C*D - A*F) / (B*D - A*E)
    z = anchor1_pos[2]  # Z coordinate remains the same as anchors
    
    return x, y, z

def process_incoming_data(json_data):
    """
    Process the JSON data received from anchors and calculate position if possible.
    
    Args:
        json_data: JSON data containing distance measurements
    """
    global distance_from_anchor_1, distance_from_anchor_2, distance_from_anchor_3, latest_tag_position

    try:
        # Ensure required keys exist
        if not all(k in json_data for k in ("device_address", "distance")):
            print("Invalid JSON format or missing keys.")
            return
        
        device_address = json_data.get("device_address")
        distance_str = json_data.get("distance")

        # Validate the distance format
        if not isinstance(distance_str, str) or "cm" not in distance_str:
            print(f"Invalid distance format: {distance_str}")
            return
        
        # Extract distance value
        distance_value = float(distance_str.replace(" cm", "").strip())

        # Update respective distances based on device address
        if device_address == "10":
            distance_from_anchor_1 = distance_value
            print(f"Anchor 1 distance updated to: {distance_from_anchor_1} cm")
        elif device_address == "11":
            distance_from_anchor_2 = distance_value
            print(f"Anchor 2 distance updated to: {distance_from_anchor_2} cm")
        elif device_address == "12":
            distance_from_anchor_3 = distance_value
            print(f"Anchor 3 distance updated to: {distance_from_anchor_3} cm")

        # Calculate tag position if all distances are available
        if all(distance is not None for distance in [distance_from_anchor_1, distance_from_anchor_2, distance_from_anchor_3]):
            tag_position = calculate_position(
                ANCHOR_1_POSITION, ANCHOR_2_POSITION, ANCHOR_3_POSITION, 
                distance_from_anchor_1, distance_from_anchor_2, distance_from_anchor_3
            )

            if tag_position:
                print(f"Tag position calculated at: ({tag_position[0]:.2f}, {tag_position[1]:.2f}, {tag_position[2]:.2f}) cm")
                latest_tag_position = tag_position
            else:
                print("No valid solution found for tag position.")
    except Exception as e:
        print(f"Error processing incoming JSON data: {e}")

def send_polling_update(polling_period_ms):
    """
    Send polling period update to all anchors.
    
    Args:
        polling_period_ms: Polling period in milliseconds
    """
    polling_message = json.dumps({"polling_period": polling_period_ms})
    for anchor_ip, anchor_port in ANCHOR_IPS:
        socket_connection.sendto(polling_message.encode('utf-8'), (anchor_ip, anchor_port))
    print(f"Sent polling period update to anchors: {polling_message}")

def main():
    """
    Main function that listens for UDP packets and processes them.
    """
    print("Starting location tracking system...")
    print(f"Anchor 1 position: {ANCHOR_1_POSITION}")
    print(f"Anchor 2 position: {ANCHOR_2_POSITION}")
    print(f"Anchor 3 position: {ANCHOR_3_POSITION}")
    
    # Default polling period in milliseconds
    default_polling_period = 100
    send_polling_update(default_polling_period)
    
    # Main loop for UDP listening
    try:
        while True:
            # Receive data from the anchors
            data, addr = socket_connection.recvfrom(1024)  # Buffer size is 1024 bytes
            ip, port = addr
            
            try:
                # Decode and parse the JSON data
                json_data = json.loads(data.decode('utf-8'))
                print(f"Received from {ip}:{port}:\n{json.dumps(json_data, indent=4)}")
                
                # Process the data
                process_incoming_data(json_data)

            except json.JSONDecodeError:
                print("Invalid JSON received:")
                print(data.decode('utf-8'))
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        socket_connection.close()
        print("Socket closed.")

if __name__ == "__main__":
    main()