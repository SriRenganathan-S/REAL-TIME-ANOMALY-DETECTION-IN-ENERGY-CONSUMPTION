import time
import json
import random
from kafka import KafkaProducer
from datetime import datetime

# CONFIGURATION
KAFKA_TOPIC = "telemetry-raw"
METER_ID = "Universal_Meter_001"

# SETUP KAFKA
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda x: json.dumps(x).encode('utf-8')
)

print(f"[METER] Universal Smart Meter {METER_ID} Started...")
print("[INFO] Simulating realistic home energy usage (98% Normal / 2% Anomalies)...")

while True:
    # 1. RAW PHYSICS GENERATION
    voltage = 230 + random.uniform(-1, 1)  # Very stable voltage
    frequency = 50 + random.uniform(-0.02, 0.02) # Very stable freq
    power_factor = random.uniform(0.90, 0.99)
    
    # DECIDE SCENARIO (Weighted Probability)
    rand_val = random.random()

    # --- Scenario A: Normal Usage (90% chance) ---
    if rand_val < 0.90:
        current = random.uniform(1.5, 2.5)  # 300W - 600W (TV, Lights)
        status_label = "Normal"

    # --- Scenario B: High Load - SAFE (8% chance) ---
    # TELLS AI: "High power is okay if it's just an Appliance"
    elif rand_val < 0.98:
        current = random.uniform(8.0, 12.0) # 2000W - 3000W (AC, Kettle)
        status_label = "High Load (Safe)"
        print(f"[APPLIANCE] AC/Kettle running...")

    # --- Scenario C: CRITICAL FAULT (2% chance) ---
    else:
        fault_type = random.choice(['short_circuit', 'freq_drop'])
        
        if fault_type == 'short_circuit':
            print("[FAULT] Short Circuit!")
            current = 35.0  # Massive Current Spike (8000W+)
            status_label = "CRITICAL FAULT"
        else:
            print("[FAULT] Grid Frequency Drop!")
            frequency = 48.5 # Dangerously low
            current = random.uniform(1.5, 2.5)
            status_label = "GRID FAILURE"

    # 2. CALCULATE POWER
    power_w = voltage * current * power_factor

    # 3. SEND DATA
    data = {
        "meter_id": METER_ID,
        "timestamp": datetime.now().isoformat(),
        "voltage_v": round(voltage, 2),
        "current_a": round(current, 2),
        "power_w": round(power_w, 2),
        "frequency_hz": round(frequency, 3),
        "label": status_label # Helper for debugging
    }

    producer.send(KAFKA_TOPIC, value=data)
    
    # Print Logic (Clean Output)
    if status_label == "Normal":
        print(f"Sent: {data['power_w']}W | {data['frequency_hz']}Hz")
    else:
        print(f"[ALERT] {status_label}: {data['power_w']}W")
        
    time.sleep(1)