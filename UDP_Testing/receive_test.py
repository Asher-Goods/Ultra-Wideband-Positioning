import socket
import json
import math

# Server configuration
UDP_IP = "0.0.0.0"  # Listen on all available interfaces
UDP_PORT = 50000    # Match the port number used in the ESP32 code

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

print(f"Listening for UDP packets on {UDP_IP}:{UDP_PORT}...")

# Variables to store the latest distances
distance_7 = None
distance_8 = None


def calculate_tag_position(anchor1, anchor2, distance1, distance2):
    """
    Calculate the position of a tag given two anchor points and distances.
    
    :param anchor1: Tuple (x, y) of the first anchor's position
    :param anchor2: Tuple (x, y) of the second anchor's position
    :param distance1: Distance from anchor1 to the tag
    :param distance2: Distance from anchor2 to the tag
    :return: Tuple (x, y) of the tag's position, or None if no solution exists
    """
    x1, y1 = anchor1
    x2, y2 = anchor2

    # Calculate the x-coordinate
    try:
        x = (x1**2 + y1**2 - x2**2 - y2**2 + distance2**2 - distance1**2) / (2 * (x1 - x2))

        # Calculate the y-coordinate
        y_term = math.sqrt(distance1**2 - (x - x1)**2)
        y1_candidate = y1 + y_term
        y2_candidate = y1 - y_term

        # Choose the candidate that makes the most sense geometrically
        mid_y = (y1_candidate + y2_candidate) / 2
        y = y1_candidate if abs(y1_candidate - mid_y) < abs(y2_candidate - mid_y) else y2_candidate

        return x, y
    except ValueError:
        # Handle invalid geometry calculations
        return None


def process_incoming_data(json_data):
    global distance_7, distance_8

    # Parse JSON
    try:
        device_address = json_data.get("device_address")
        distance_str = json_data.get("distance")
        # Remove 'cm' from the string and convert it to float
        distance_value = float(distance_str.replace(" cm", "").strip())

        # Update respective distances
        if device_address == "7":
            distance_7 = distance_value
            print(f"Anchor 7 distance updated to: {distance_7} cm")
        elif device_address == "8":
            distance_8 = distance_value
            print(f"Anchor 8 distance updated to: {distance_8} cm")

        # Attempt to calculate tag position if both distances are available
        if distance_7 is not None and distance_8 is not None:
            # Define anchor positions (you can adjust these coordinates)
            anchor_1_position = (0, 0)
            anchor_2_position = (350, 0)

            tag_position = calculate_tag_position(
                anchor_1_position, anchor_2_position, distance_7, distance_8
            )

            if tag_position:
                print(f"Tag position calculated at: {tag_position}")
            else:
                print("No valid solution found for tag position.")
    except Exception as e:
        print(f"Error processing incoming JSON data: {e}")


while True:
    # Receive data from the ESP32
    data, addr = sock.recvfrom(1024)  # Buffer size is 1024 bytes
    try:
        # Decode and parse the JSON data
        json_data = json.loads(data.decode('utf-8'))
        print(json.dumps(json_data, indent=4))
        
        # Process the data
        process_incoming_data(json_data)

    except json.JSONDecodeError:
        print("Invalid JSON received:")
        print(data.decode('utf-8'))
