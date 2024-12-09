import socket
import json
import math
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.patches as patches 
import matplotlib.pyplot as plt

# default anchor positions
anchor_1_position = (0, 0)
anchor_2_position = (350, 0)

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
distance_7 = None
distance_8 = None
latest_tag_position = None  # Variable to store the latest calculated tag position


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

    try:
        # Calculate the x-coordinate
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


def process_incoming_data(json_data, ui):
    global distance_7, distance_8, latest_tag_position

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


            tag_position = calculate_tag_position(
                ui.anchor_1_position, ui.anchor_2_position, distance_7, distance_8
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

        # Set up matplotlib figure and canvas
        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.fig, master)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=1)

        # Set up axes limits
        self.ax.set_xlim(-300, 500)
        self.ax.set_ylim(-300, 1250)
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

        # Anchor 2 inputs
        tk.Label(input_frame, text="Anchor 2 (x, y):").grid(row=1, column=0, padx=5, pady=5)
        self.anchor_2_x_entry = tk.Entry(input_frame, width=10)
        self.anchor_2_x_entry.insert(0, str(self.anchor_2_position[0]))
        self.anchor_2_x_entry.grid(row=1, column=1, padx=5, pady=5)
        self.anchor_2_y_entry = tk.Entry(input_frame, width=10)
        self.anchor_2_y_entry.insert(0, str(self.anchor_2_position[1]))
        self.anchor_2_y_entry.grid(row=1, column=2, padx=5, pady=5)

        # Update button
        tk.Button(input_frame, text="Update Anchors", command=self.update_anchor_positions).grid(
            row=2, column=0, columnspan=3, pady=10
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
            ]
            self.anchor_2_position = [
                float(self.anchor_2_x_entry.get()),
                float(self.anchor_2_y_entry.get()),
            ]

            # Redraw the background and anchors
            self.ax.clear()
            self.ax.set_xlim(-300, 500)
            self.ax.set_ylim(-300, 1250)
            self.ax.set_xlabel("X Coordinate")
            self.ax.set_ylabel("Y Coordinate")
            self.ax.grid()
            self.draw_background_squares()

            print(f"Anchor positions updated to: {self.anchor_1_position}, {self.anchor_2_position}")

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
        self.ax.add_patch(patches.Rectangle((0, 0), -200, 200, linewidth=0, edgecolor='blue', facecolor='blue', alpha=0.3))
        self.ax.add_patch(patches.Rectangle((-200, 200), 200, 300, linewidth=0, edgecolor='red', facecolor='red', alpha=0.3))
        self.ax.add_patch(patches.Rectangle((0, 0), 375, 300, linewidth=0, edgecolor='green', facecolor='green', alpha=0.3))
        self.ax.add_patch(patches.Rectangle((0, 300), 100, 700, linewidth=0, edgecolor='yellow', facecolor='yellow', alpha=0.3))
        self.ax.add_patch(patches.Rectangle((-200, 500), 200, 150, linewidth=0, edgecolor='yellow', facecolor='yellow', alpha=0.3))
        self.ax.add_patch(patches.Rectangle((100, 300), 275, 400, linewidth=0, edgecolor='purple', facecolor='purple', alpha=0.3))
        self.ax.add_patch(patches.Rectangle((100, 700), 275, 500, linewidth=0, edgecolor='brown', facecolor='brown', alpha=0.3))
        self.ax.add_patch(patches.Rectangle((-200, 650), 200, 550, linewidth=0, edgecolor='orange', facecolor='orange', alpha=0.3))

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
        self.current_tag_point = self.ax.plot(position[0], -position[1], 'ro')[0]
        # Add new annotation
        self.current_annotation = self.ax.annotate(
            f"Tag ({position[0]:.2f}, {position[1]:.2f})",
            (position[0], -position[1]),
            textcoords="offset points",
            xytext=(5, 5),
            ha="center",
        )

    def update_plot(self):
        """
        Periodically called to check for updates in the latest tag position and redraw the dynamic plot.
        """
        # Avoid clearing the permanent background - only draw dynamic elements
        self.ax.set_xlim(-300, 500)
        self.ax.set_ylim(-300, 1250)

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
