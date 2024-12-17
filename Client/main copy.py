import socket
import json
import math
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.patches as patches 
import matplotlib.pyplot as plt
import numpy as np

# default anchor positions
anchor_1_position = (0, 0, 90)
anchor_2_position = (660, 0, 90)
anchor_3_position = (250, 600, 90)

# Server configuration
UDP_IP = "0.0.0.0"  # Listen on all available interfaces
UDP_PORT = 50000  # Match the port number used in the ESP32 code

# Anchor addresses (example IPs and ports)
ANCHOR_IPS = [("192.168.1.170", 50000), ("192.168.1.171", 50000), ("192.168.1.173", 50000)]

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

print(f"Listening for UDP packets on {UDP_IP}:{UDP_PORT}...")

# Variables to store the latest distances
distance_1 = None
distance_2 = None
distance_3 = None
latest_tag_position = None  # Variable to store the latest calculated tag position


def trilateration(anchor1, anchor2, anchor3, distance1, distance2, distance3):
    A = 2*anchor2[0] - 2*anchor1[0]
    B = 2*anchor2[1] - 2*anchor1[1]
    C = distance1**2 - distance2**2 - anchor1[0]**2 + anchor2[0]**2 - anchor1[1]**2 + anchor2[1]**2
    D = 2*anchor3[0] - 2*anchor2[0]
    E = 2*anchor3[1] - 2*anchor2[1]
    F = distance2**2 - distance3**2 - anchor2[0]**2 + anchor3[0]**2 - anchor2[1]**2 + anchor3[1]**2
    x = (C*E - F*B) / (E*A - B*D)
    y = (C*D - A*F) / (B*D - A*E)
    z = anchor1[2]
    return x,y,z



def process_incoming_data(json_data, ui):
    global distance_1, distance_2, distance_3, latest_tag_position

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
        
        # Process distance
        distance_value = float(distance_str.replace(" cm", "").strip())

        # Update respective distances
        # Anchor 1 = Device address 7
        if device_address == "7":
            distance_1 = distance_value
            print(f"Anchor 1 distance updated to: {distance_1} cm")
        # Anchor 2 = Device address 8
        elif device_address == "8":
            distance_2 = distance_value
            print(f"Anchor 2 distance updated to: {distance_2} cm")
        # Anchor 3 = Device address 10
        elif device_address == "10":
            distance_3 = distance_value
            print(f"Anchor 3 distance updated to: {distance_3} cm")

        # Attempt to calculate tag position if both distances are available
        if distance_1 is not None and distance_2 is not None and distance_3 is not None:
            # Define anchor positions (you can adjust these coordinates)

            tag_position = trilateration(
                ui.anchor_1_position, ui.anchor_2_position, ui.anchor_3_position, distance_1, distance_2, distance_3
            )

            if tag_position:
                print(f"Tag position calculated at: {tag_position}")
                latest_tag_position = tag_position
            else:
                print("No valid solution found for tag position.")
    except Exception as e:
        print(f"Error processing incoming JSON data: {e}")


# Set up the UI with matplotlib integration
class TagPositionUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Tag Position UI Grid")
        self.latest_position = None
        self.polling_period = 100  # Default polling period in milliseconds

        # Default anchor positions
        self.anchor_1_position = list(anchor_1_position)  # Use a mutable list
        self.anchor_2_position = list(anchor_2_position)
        self.anchor_3_position = list(anchor_3_position)

        # Set up matplotlib figure and canvas
        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.fig, master)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=1)

        # Set up axes limits
        self.ax.set_xlim(-300, 800)
        self.ax.set_ylim(-300, 1400)
        self.ax.set_xlabel("X Coordinate")
        self.ax.set_ylabel("Y Coordinate")
        self.ax.grid()

        # Draw background squares once
        self.draw_background_squares()

        # Input fields for anchor positions
        self.create_anchor_position_inputs()

        # Create polling period slider
        self.create_polling_slider()

        # References for dynamically plotted elements
        self.current_tag_point = None
        self.current_annotation = None

        # Call the update function periodically
        self.master.after(100, self.update_plot)

    def create_anchor_position_inputs(self):
        """
        Create input fields for changing anchor positions dynamically.
        """
        input_frame = tk.Frame(self.master)
        input_frame.pack(fill=tk.X)

        # Anchor 1 inputs
        tk.Label(input_frame, text="Anchor 1 (x, y):").grid(row=0, column=0, padx=5, pady=5)
        self.anchor_1_x_entry = tk.Entry(input_frame, width=10)
        self.anchor_1_x_entry.insert(0, str(self.anchor_1_position[0]))
        self.anchor_1_x_entry.grid(row=0, column=1, padx=5, pady=5)
        self.anchor_1_y_entry = tk.Entry(input_frame, width=10)
        self.anchor_1_y_entry.insert(0, str(self.anchor_1_position[1]))
        self.anchor_1_y_entry.grid(row=0, column=2, padx=5, pady=5)
        self.anchor_1_z_entry = tk.Entry(input_frame, width=10)
        self.anchor_1_z_entry.insert(0, str(self.anchor_1_position[2]))
        self.anchor_1_z_entry.grid(row=0, column=3, padx=5, pady=5)

        # Anchor 2 inputs
        tk.Label(input_frame, text="Anchor 2 (x, y):").grid(row=1, column=0, padx=5, pady=5)
        self.anchor_2_x_entry = tk.Entry(input_frame, width=10)
        self.anchor_2_x_entry.insert(0, str(self.anchor_2_position[0]))
        self.anchor_2_x_entry.grid(row=1, column=1, padx=5, pady=5)
        self.anchor_2_y_entry = tk.Entry(input_frame, width=10)
        self.anchor_2_y_entry.insert(0, str(self.anchor_2_position[1]))
        self.anchor_2_y_entry.grid(row=1, column=2, padx=5, pady=5)
        self.anchor_2_z_entry = tk.Entry(input_frame, width=10)
        self.anchor_2_z_entry.insert(0, str(self.anchor_2_position[2]))
        self.anchor_2_z_entry.grid(row=1, column=3, padx=5, pady=5)

        # Anchor 3 inputs
        tk.Label(input_frame, text="Anchor 3 (x, y):").grid(row=2, column=0, padx=5, pady=5)
        self.anchor_3_x_entry = tk.Entry(input_frame, width=10)
        self.anchor_3_x_entry.insert(0, str(self.anchor_3_position[0]))
        self.anchor_3_x_entry.grid(row=2, column=1, padx=5, pady=5)
        self.anchor_3_y_entry = tk.Entry(input_frame, width=10)
        self.anchor_3_y_entry.insert(0, str(self.anchor_3_position[1]))
        self.anchor_3_y_entry.grid(row=2, column=2, padx=5, pady=5)
        self.anchor_3_z_entry = tk.Entry(input_frame, width=10)
        self.anchor_3_z_entry.insert(0, str(self.anchor_3_position[2]))
        self.anchor_3_z_entry.grid(row=2, column=3, padx=5, pady=5)

        # Update button
        tk.Button(input_frame, text="Update Anchors", command=self.update_anchor_positions).grid(
            row=3, column=0, columnspan=3, pady=10
        )

    def update_anchor_positions(self):
        """
        Update the anchor positions based on user input and redraw the plot.
        """
        try:
            # Get new anchor positions from the input fields
            self.anchor_1_position = [
                float(self.anchor_1_x_entry.get()),
                float(self.anchor_1_y_entry.get()),
                float(self.anchor_1_z_entry.get()),
            ]
            self.anchor_2_position = [
                float(self.anchor_2_x_entry.get()),
                float(self.anchor_2_y_entry.get()),
                float(self.anchor_2_z_entry.get()),
            ]
            self.anchor_3_position = [
                float(self.anchor_3_x_entry.get()),
                float(self.anchor_3_y_entry.get()),
                float(self.anchor_3_z_entry.get()),
            ]

            # Redraw the background and anchors
            self.ax.clear()
            self.ax.set_xlim(-300, 800)
            self.ax.set_ylim(-300, 1400)
            self.ax.set_xlabel("X Coordinate")
            self.ax.set_ylabel("Y Coordinate")
            self.ax.grid()
            self.draw_background_squares()

            print(f"Anchor positions updated to: {self.anchor_1_position}, {self.anchor_2_position}, {self.anchor_3_position}")

            # Redraw tag position if available
            if latest_tag_position:
                self.update_tag_position(latest_tag_position)

            self.canvas.draw()
        except ValueError:
            print("Invalid input for anchor positions. Please enter numeric values.")

    def draw_background_squares(self):
        """
        Draw background squares that remain constant and act as a permanent background.
        """
        # Add background rectangles as before (unchanged)
        # self.ax.add_patch(patches.Rectangle((0, 0), -200, 200, linewidth=0, edgecolor='blue', facecolor='blue', alpha=0.3))
        # self.ax.add_patch(patches.Rectangle((-200, 200), 200, 300, linewidth=0, edgecolor='red', facecolor='red', alpha=0.3))
        # self.ax.add_patch(patches.Rectangle((0, 0), 375, 300, linewidth=0, edgecolor='green', facecolor='green', alpha=0.3))
        # self.ax.add_patch(patches.Rectangle((0, 300), 100, 700, linewidth=0, edgecolor='yellow', facecolor='yellow', alpha=0.3))
        # self.ax.add_patch(patches.Rectangle((-200, 500), 200, 150, linewidth=0, edgecolor='yellow', facecolor='yellow', alpha=0.3))
        # self.ax.add_patch(patches.Rectangle((100, 300), 275, 400, linewidth=0, edgecolor='purple', facecolor='purple', alpha=0.3))
        # self.ax.add_patch(patches.Rectangle((100, 700), 275, 500, linewidth=0, edgecolor='brown', facecolor='brown', alpha=0.3))
        # self.ax.add_patch(patches.Rectangle((-200, 650), 200, 550, linewidth=0, edgecolor='orange', facecolor='orange', alpha=0.3))

        # Redraw anchors
        self.ax.plot(self.anchor_1_position[0], self.anchor_1_position[1], 'rs', markersize=10)
        self.ax.annotate(
            "Anchor 1",
            (self.anchor_1_position[0], self.anchor_1_position[1]),
            textcoords="offset points",
            xytext=(5, -15),
            ha="center",
        )
        self.ax.plot(self.anchor_2_position[0], self.anchor_2_position[1], 'rs', markersize=10)
        self.ax.annotate(
            "Anchor 2",
            (self.anchor_2_position[0], self.anchor_2_position[1]),
            textcoords="offset points",
            xytext=(5, -15),
            ha="center",
        )
        self.ax.plot(self.anchor_3_position[0], self.anchor_3_position[1], 'rs', markersize=10)
        self.ax.annotate(
            "Anchor 3",
            (self.anchor_3_position[0], self.anchor_3_position[1]),
            textcoords="offset points",
            xytext=(5, -15),
            ha="center",
        )

    def create_polling_slider(self):
        slider_frame = tk.Frame(self.master)
        slider_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(slider_frame, text="Polling Period (ms):").pack(side=tk.LEFT)
        self.polling_slider = tk.Scale(
            slider_frame,
            from_=10,
            to=60000,
            orient=tk.HORIZONTAL,
            resolution=50,
            command=self.update_polling_period,
        )
        self.polling_slider.set(self.polling_period)
        self.polling_slider.pack(fill=tk.X, expand=True)

    def update_polling_period(self, value):
        self.polling_period = int(value)
        print(f"Polling period updated to: {self.polling_period} ms")

        # Send the updated polling period to the anchors
        polling_message = json.dumps({"polling_period": self.polling_period})
        for anchor_ip, anchor_port in ANCHOR_IPS:
            sock.sendto(polling_message.encode('utf-8'), (anchor_ip, anchor_port))
        print(f"Sent polling period update to anchors: {polling_message}")

    def update_tag_position(self, position):
        """
        Updates the red dot and its annotation for the tag position dynamically.
        Clears the previous red dot and annotation if they exist.
        """
        # Remove the previous red dot and annotation if they exist
        if self.current_tag_point:
            self.current_tag_point.remove()
            self.current_tag_point = None
        if self.current_annotation:
            self.current_annotation.remove()
            self.current_annotation = None

        # Plot new red dot
        self.current_tag_point = self.ax.plot(position[0], position[1], 'ro')[0]
        # Add new annotation
        self.current_annotation = self.ax.annotate(
            f"Tag ({position[0]:.2f}, {position[1]:.2f})",
            (position[0], position[1]),
            textcoords="offset points",
            xytext=(5, 5),
            ha="center",
        )

    def update_plot(self):
        """
        Periodically called to check for updates in the latest tag position and redraw the dynamic plot.
        """
        # Avoid clearing the permanent background - only draw dynamic elements
        self.ax.set_xlim(-300, 800)
        self.ax.set_ylim(-300, 1400)

        # Redraw the tag position if available
        if latest_tag_position:
            self.update_tag_position(latest_tag_position)

        # Redraw only the dynamic parts
        self.canvas.draw()
        self.master.after(100, self.update_plot)  # Reschedule this function


# Main loop for receiving UDP packets and starting UI
def main():
    # Start Tkinter UI
    root = tk.Tk()
    ui = TagPositionUI(root)

    # Thread or main loop for UDP listening
    def udp_listener():
        while True:
            # Receive data from the ESP32
            data, addr = sock.recvfrom(1024)  # Buffer size is 1024 bytes
            ip, port = addr
            try:
                # Decode and parse the JSON data
                json_data = json.loads(data.decode('utf-8'))
                print(f"Received from {ip}:{port}:\n{json.dumps(json_data, indent=4)}")
                
                # Process the data
                process_incoming_data(json_data, ui)

            except json.JSONDecodeError:
                print("Invalid JSON received:")
                print(data.decode('utf-8'))

    import threading
    listener_thread = threading.Thread(target=udp_listener, daemon=True)
    listener_thread.start()

    # Start the Tkinter mainloop
    root.mainloop()


if __name__ == "__main__":
    main()
