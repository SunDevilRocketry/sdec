import pandas as pd

# Define the file path and column labels
file_path = 'output/flight_comp_rev2_sensor_data.txt'  # Update this to the actual file path
columns = [
    "accXOffset", "accYOffset", "accZOffset", "gyroXOffset", "gyroYOffset", "gyroZOffset", "rp_servo1", "rp_servo2", "time", "accX", "accY", "accZ", "gyroX", "gyroY", "gyroZ",
    "magX", "magY", "magZ", "imut", 
    "accXconv", "accYconv", "accZconv", "gyroXconv", "gyroYconv", "gyroZconv",
    "rollDeg", "pitchDeg", "rollRate", "pitchRate", "velo", "pos", "pres", "temp"
]

# Load the data with specified column names
data = pd.read_csv(file_path, sep="\t", header=None, names=columns)

# Display the first few rows to verify
print(data.head())

# Optionally, save to a new CSV file
data.to_csv('parsed_sensor_data_2.csv', index=False)