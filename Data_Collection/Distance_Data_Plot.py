import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Data from the inputs, organized by distance marker
data = {
    "1m": [133, 118, 130, 113, 123, 127, 143, 140],
    "2m": [230, 214, 236, 232, 221, 219, 237, 206],
    "3m": [378, 387, 350, 341, 387, 395],
    "4m": [448, 367, 441, 435, 452, 431, 477],
    "5m": [562, 616, 650, 602, 625, 603, 553],
    "6m": [651, 649, 650, 630, 632, 702, 629, 637],
    "7m": [800, 836, 797, 817, 831, 801, 811, 845],
    "8m": [890, 931, 926, 846, 922, 843, 845, 855, 876],
    "9m": [1052, 1054, 1041, 1047, 1045, 1056, 1023, 1024, 1024],
    "10m": [1110, 1141, 1131, 1107, 1119, 1111, 1111, 1116],
    "11m": [1228, 1212, 12215, 1211, 1244, 1217, 1214, 1200],  # Note: 12215 might be a typo
    "12m": [1300, 1319, 1285, 1291, 1294, 1298, 1289, 1318],
    "13m": [1405, 1412, 1404, 1406, 1403, 1409, 1411, 1403, 1405, 1412],
    "14m": [1515, 1516, 1504, 1509, 1551, 1510, 1538, 1550, 1523, 1526, 1482],
    "15m": [1485, 1582, 1610, 1617, 1484, 1589, 1605, 1581, 1596, 1607],
    "16m": [1658, 1684, 1673, 1670, 1684, 1688, 1699, 1690],
    "17m": [1807, 1831, 1842, 1828, 1830, 1814, 1828, 1798],
    "18m": [1931, 1928, 1913, 1909, 1918, 1975, 1980, 1920],
    "19m": [2019, 2059, 2053, 2033, 2022, 2024, 2031, 2059],
    "20m": [2108, 2149, 2135, 2111],
    "21m": [2266, 2289, 2206],
    "22m": [2311, 2287, 2292],
    "23m": [2413, 2422, 2374],
    "24m": [2475, 2476, 2477, 2472],
    "25m": [2602, 2632, 2612, 2627, 2622],
    "26m": [2749, 2681, 2652, 2687, 2702, 2716],
    "27m": [2773, 2801, 2726, 2783],
    "28m": [2803, 2905, 2899, 2903, 2855],
    "29m": [2817, 2979, 2970, 2950, 2991]
}

# Check for and fix the potential typo in the 11m data
if 12215 in data["11m"]:
    print("Warning: Found value 12215 in 11m data, which may be a typo. For plotting purposes, replacing with 1215.")
    data["11m"] = [x if x != 12215 else 1215 for x in data["11m"]]

# Calculate the means for each distance marker
distances = []
expected_values = []
actual_means = []
raw_data = []

for marker, values in sorted(data.items(), key=lambda x: int(x[0].rstrip('m'))):
    distance = int(marker.rstrip('m'))
    mean_value = np.mean(values)
    
    distances.append(distance)
    expected_values.append(distance * 100)  # Expected value is the distance times 100
    actual_means.append(mean_value)
    
    # Add raw data points for scatter plot
    for value in values:
        raw_data.append((distance, value))

# Convert raw data to arrays for plotting
raw_x, raw_y = zip(*raw_data)

# Create a DataFrame for easy data manipulation and display
df = pd.DataFrame({
    'Distance (m)': distances,
    'Expected Value (m*100)': expected_values,
    'Actual Mean': actual_means,
    'Difference': [a - e for a, e in zip(actual_means, expected_values)],
    'Percent Difference': [((a - e) / e * 100) for a, e in zip(actual_means, expected_values)]
})

# Print the data table
print(df.to_string(index=False))

# Create a nice looking plot
plt.figure(figsize=(12, 8))

# Plot raw data as scatter points
plt.scatter(raw_x, raw_y, color='lightgray', alpha=0.5, label='Raw Data')

# Plot expected and actual lines
plt.plot(distances, expected_values, 'b-', linewidth=2, label='Expected (distance × 100)')
plt.plot(distances, actual_means, 'r-', linewidth=2, label='Actual (mean of measurements)')

# Fill the area between the lines to highlight the difference
plt.fill_between(distances, expected_values, actual_means, color='yellow', alpha=0.3)

# Add labels and title
plt.xlabel('Distance (m)', fontsize=12)
plt.ylabel('Value', fontsize=12)
plt.title('Comparison of Expected vs. Actual Values by Distance', fontsize=14)
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend(fontsize=12)

# Add text labels for the y-values at a few key points (not all to avoid clutter)
label_indexes = [0, 9, 19, 28]  # Index positions to label (1m, 10m, 20m, 29m)
for idx in label_indexes:
    plt.text(distances[idx], expected_values[idx], f"{expected_values[idx]:.0f}", 
             color='blue', fontsize=10, va='bottom')
    plt.text(distances[idx], actual_means[idx], f"{actual_means[idx]:.0f}", 
             color='red', fontsize=10, va='top')

# Set tight layout and save the figure
plt.tight_layout()
plt.savefig('distance_value_comparison.png', dpi=300)

# Show summary statistics
print("\nSummary:")
print(f"Average difference (Actual - Expected): {np.mean(df['Difference']):.2f}")
print(f"Average percent difference: {np.mean(df['Percent Difference']):.2f}%")
print(f"Maximum positive difference: {max(df['Difference']):.2f} at {df.loc[df['Difference'].idxmax(), 'Distance (m)']}m")
print(f"Maximum negative difference: {min(df['Difference']):.2f} at {df.loc[df['Difference'].idxmin(), 'Distance (m)']}m")

plt.show()

# If you want to see the exact differences, uncomment these lines:
# plt.figure(figsize=(12, 6))
# plt.bar(distances, df['Difference'])
# plt.axhline(y=0, color='r', linestyle='-')
# plt.xlabel('Distance (m)')
# plt.ylabel('Difference (Actual - Expected)')
# plt.title('Difference Between Actual and Expected Values')
# plt.grid(True, axis='y', linestyle='--', alpha=0.7)
# plt.tight_layout()
# plt.show()