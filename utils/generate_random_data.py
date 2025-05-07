"""

import random
import csv
from datetime import datetime, timedelta
from typing import List, Tuple, Dict, Any

# Real-world example locations (latitude, longitude)
locations = [
    (12.9715, 77.5973),  # Bangalore
    (28.6139, 77.2090),  # Delhi
    (19.0760, 72.8777),  # Mumbai
    (13.0827, 80.2707),  # Chennai
    (22.5726, 88.3639),  # Kolkata
]
# Function to generate historical/bulk data
def generate_random_sensor_data(num_entries: int = 100) -> List[List[Any]]:
    data = []
    current_time = datetime.now()

    for _ in range(num_entries):
        timestamp = current_time.strftime("%Y-%m-%d %H:%M:%S")
        location = random.choice(locations)
        water_level = round(random.uniform(0.5, 5.0), 2)
        flow_rate = round(random.uniform(0.1, 3.0), 2)
        pressure = round(random.uniform(0.5, 2.0), 2)
        vibration = round(random.uniform(0.0, 1.0), 2)
        gas_concentration = round(random.uniform(0.0, 100.0), 2)
        proximity = round(random.uniform(0.0, 1.0), 2)
        blockage_status = random.choice([0, 1])  # 0 = No Blockage, 1 = Blockage

        data.append([
            timestamp,
            f"{location[0]},{location[1]}",
            water_level,
            flow_rate,
            pressure,
            vibration,
            gas_concentration,
            proximity,
            blockage_status
        ])

        current_time += timedelta(seconds=5)

    return data
# Function to save data into CSV
def save_to_csv(data: List[List[Any]], filename: str = "sensor_data.csv") -> None:
    headers = [
        "timestamp", "location", "water_level", "flow_rate",
        "pressure", "vibration", "gas_concentration", "proximity", "blockage_status"
    ]
    with open(filename, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        writer.writerows(data)
def get_live_sensor_data():
    sensors = ['Water Level', 'Flow Rate', 'Pressure', 'Vibration', 'Gas Concentration', 'Proximity']

    is_blockage = random.random() < 0.2  # 20% chance of blockage
    triggered_sensor = random.choice(sensors) if is_blockage else '---'

    sensor_data = {
        'location': f'Zone-{random.randint(1, 10)}',
        'water_level': round(random.uniform(10, 100), 2),
        'flow_rate': round(random.uniform(0, 50), 2),
        'pressure': round(random.uniform(50, 200), 2),
        'vibration': round(random.uniform(0, 10), 2),
        'gas_concentration': round(random.uniform(0, 100), 2),
        'proximity': round(random.uniform(0, 20), 2),
        'triggered_sensor': triggered_sensor
    }

    return sensor_data
# Main execution block
if __name__ == "__main__":
    data = generate_random_sensor_data(500)
    save_to_csv(data)
    print("✅ 500 sensor data entries generated and saved to 'sensor_data.csv'")

    # Example live data
    live_data = get_live_sensor_data()
    print("Live Sensor Data Example:")
    print(live_data)
"""
"""import random
import serial
import time

# ✅ Setup Arduino Serial connection
arduino = serial.Serial(port='COM5', baudrate=9600, timeout=1)
time.sleep(0.5)  # wait for connection


def read_real_water_level():
    line = arduino.readline().decode('utf-8').strip()
    if line.startswith("Water Level Value:"):
        value = int(line.split(":")[1].strip())
        return value
    else:
        return None


def get_live_sensor_data():
    sensors = ['Water Level', 'Flow Rate', 'Pressure', 'Vibration', 'Gas Concentration', 'Proximity']

    # ✅ Real Water Level from Arduino
    real_water_level = read_real_water_level()
    if real_water_level is None:
        real_water_level = 0  # fallback if no read

    is_blockage = random.random() < 0.2  # 20% chance of blockage
    triggered_sensor = random.choice(sensors) if is_blockage else '---'

    sensor_data = {
        'location': f'Zone-{random.randint(1, 10)}',
        'water_level': real_water_level,  # ✅ Real data here!
        'flow_rate': round(random.uniform(0, 50), 2),
        'pressure': round(random.uniform(50, 200), 2),
        'vibration': round(random.uniform(0, 10), 2),
        'gas_concentration': round(random.uniform(0, 100), 2),
        'proximity': round(random.uniform(0, 20), 2),
        'triggered_sensor': triggered_sensor
    }

    return sensor_data


# Test run
if __name__ == "__main__":
    while True:
        live_data = get_live_sensor_data()
        print(live_data)
        time.sleep(0.5)
""""""
import random
import datetime
import time
import serial
from utils.auto_detect_com import get_arduino_serial

# Get serial connection to Arduino


try:

    arduino = get_arduino_serial()
    time.sleep(2)  # wait for the serial connection to initialize
    ARDUINO_CONNECTED = True
except Exception as e:
    print(f"Arduino not connected. Using simulated data. Error: {e}")
    ARDUINO_CONNECTED = False

def get_live_sensor_data():
    if ARDUINO_CONNECTED:
        try:
            arduino.write(b'R')  # Optional: send a signal to Arduino to read data
            line = arduino.readline().decode('utf-8').strip()
            print(f"Serial Data: {line}")  # For debugging

            # Suppose Arduino sends comma-separated: water_level,flow_rate,pressure
            parts = line.split(',')

            return {
                "location": "Drainage Point A",
                "water_level": int(parts[0]),
                "flow_rate": float(parts[1]),
                "pressure": float(parts[2]),
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "triggered_sensor": "Sensor 1"
            }
        except Exception as e:
            print(f"Error reading serial data: {e}")

    # If Arduino not connected or error ➔ simulate data
    return {
        "location": "Drainage Point A",
        "water_level": random.randint(0, 100),
        "flow_rate": round(random.uniform(0.1, 5.0), 2),
        "pressure": round(random.uniform(1.0, 10.0), 2),
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "triggered_sensor": "Simulated Sensor"
    }

# Optional: for testing this file directly
if __name__ == "__main__":
    while True:
        data = get_live_sensor_data()
        print(data)
        time.sleep(2)  # every 2 seconds
"""
import random
import datetime
import time
import serial
from utils.auto_detect_com import get_arduino_serial

# Global variables
ARDUINO_CONNECTED = False
arduino = None

# ✅ Initialize Arduino connection safely
def init_arduino():
    global arduino, ARDUINO_CONNECTED
    try:
        arduino = get_arduino_serial()
        time.sleep(2)  # wait for serial connection
        ARDUINO_CONNECTED = True
        print("✅ Arduino connected!")
    except Exception as e:
        print(f"❌ Arduino not connected. Using simulated data. Error: {e}")
        ARDUINO_CONNECTED = False

# ✅ Function to get live sensor data (real or simulated)
def get_live_sensor_data():
    if ARDUINO_CONNECTED:
        try:
            arduino.write(b'R')  # Optional: command Arduino to send data
            line = arduino.readline().decode('utf-8').strip()
            print(f"Serial Data: {line}")  # For debugging

            # Expected format: water_level,flow_rate,pressure
            parts = line.split(',')
            if len(parts) == 3:
                return {
                    "location": "Drainage Point A",
                    "water_level": int(parts[0]),
                    "flow_rate": float(parts[1]),
                    "pressure": float(parts[2]),
                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "triggered_sensor": "Sensor 1"
                }
            else:
                print("⚠️ Invalid data format from Arduino. Simulating...")
        except Exception as e:
            print(f"❌ Error reading serial data: {e}")

    # ✅ Simulated data if Arduino fails
    return {
        "location": "Drainage Point A",
        "water_level": random.randint(0, 100),
        "flow_rate": round(random.uniform(0.1, 5.0), 2),
        "pressure": round(random.uniform(1.0, 10.0), 2),
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "triggered_sensor": "Simulated Sensor"
    }

# ✅ Only runs when you do ➡️ python generate_random_data.py
if __name__ == "__main__":
    init_arduino()
    while True:
        data = get_live_sensor_data()
        print(data)
        time.sleep(2)  # every 2 seconds




