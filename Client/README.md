## Summary of the Code

This Python script implements a system for receiving, processing, and visualizing distance data from anchors (e.g., ESP32 devices) in real time. The visualization uses a graphical user interface (GUI) built with **Tkinter** and integrates **matplotlib** for graphical plotting. The system listens for UDP data, computes a position from distance measurements, and dynamically visualizes the computed tag position relative to defined anchor points on a plotted coordinate grid.

---

### 🔧 **Key Features**

1. **UDP Socket Listening**
   - Listens for incoming UDP packets from specified anchor devices on `UDP_PORT=50000`.
   - Processes JSON-formatted distance data from anchors (`device_address=7` or `device_address=8`).

2. **Position Calculation**
   - Uses trilateration (`calculate_tag_position`) to compute the position of a tag based on distances from two anchor points.

3. **Dynamic GUI with Visualization**
   - Uses `matplotlib` with `tkinter` to render a 2D visualization of anchor positions, background grids, and computed tag positions.
   - Allows dynamic updates for anchor positions and tag movement visualization.

4. **UI with Real-time Updates**
   - Users can change anchor positions interactively through input fields.
   - Includes a slider for adjusting the polling period, dynamically sent to the anchors via UDP.

5. **Background Visualization**
   - Static background rectangles act as spatial references for visualization on the map.

---

### 📡 **How Data is Handled**

1. **Incoming UDP Data**
   - Listens for data packets.
   - Parses data (expected JSON) to extract distances.
   - Updates global distances for calculations.

2. **Distance to Position Calculation**
   - Computes tag position using **trilateration** between two anchor points.
   - Handles invalid geometry calculations gracefully.

3. **Visualization**
   - Displays:
     - Anchors in their current positions.
     - Dynamic tag position updates.
     - Interactive background patches for spatial reference.

---

### 🖥️ **Classes & Functions**

#### **Main Components**
1. **TagPositionUI Class**
   - Handles GUI creation, visualization, and UI interaction.
   - **Key methods:**
     - `create_anchor_position_inputs`: Adds interactive UI elements for anchor control.
     - `update_anchor_positions`: Dynamically updates the anchor positions on the plot.
     - `draw_background_squares`: Draws visual background grids on the matplotlib canvas.
     - `update_tag_position`: Dynamically updates the visualized tag's location.

2. **UDP Listener Thread**
   - Listens for incoming UDP packets.
   - Parses JSON data and invokes `process_incoming_data`.

3. **Processing Incoming Data**
   - Extracts distance information from JSON packets.
   - Updates distances and triggers trilateration-based calculations.

---

### 🚀 **Flow**

1. **Initialization**
   - Starts a UDP server bound to a port and initializes the visualization UI.
2. **Receive Data**
   - Listens for data packets on a UDP socket (`port 50000`) using a dedicated thread.
3. **Parse & Process Data**
   - Parses JSON packets.
   - Computes distances and calculates tag position via trilateration.
4. **Visualization**
   - Displays the calculated tag position using matplotlib with Tkinter.
5. **Interactive GUI**
   - Allows adjustment of anchor positions and polling periods.

---

### 🏗️ **Dependencies**
1. `socket`
2. `json`
3. `math`
4. `tkinter`
5. `matplotlib`
   - Integrated via `FigureCanvasTkAgg`.

---

### ⚙️ **Configuration**

#### Anchor Settings
- IPs for ESP32 devices are defined statically:
  ```python
  ANCHOR_IPS = [("192.168.1.170", 50000), ("192.168.1.171", 50000), ("192.168.1.173", 50000)]
  ```

#### Polling Period
- Users can adjust polling intervals using a slider (via the GUI).
- Sends updated polling intervals to anchors using UDP.

---

### 📊 **Visual Elements**

1. **Anchor Points**
   - Visual markers on the plot for anchor positions.

2. **Tag Movement**
   - A red dot (`'ro'`) that represents the dynamically computed tag position on the map.

3. **Background Rectangles**
   - Spatial context visualization overlays (grid-like areas defined by color).

---

### 🛠️ **Error Handling**

- Handles invalid JSON decoding.
- Handles invalid trilateration results gracefully.

---

### 📥 **UDP Packet Data Structure**

Expected JSON format from the anchor:

```json
{
  "device_address": "7",
  "distance": "345 cm"
}
```

---

### 🏁 **How to Run**

1. Ensure the anchors (ESP32 devices) are sending UDP packets to `UDP_PORT=50000`.
2. Run the script.
3. A GUI window will open for visualizing tag positions in real time.

---

