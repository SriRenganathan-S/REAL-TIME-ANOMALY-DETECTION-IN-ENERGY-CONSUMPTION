"""
MULTI-METER SIMULATOR - Phase 3
Simulates 5 diverse real-world meters simultaneously:
1. Apartment (150W-1500W, simple household)
2. Suburban Home (300W-4500W, typical household with AC)
3. Automobile Assembly Factory (50kW-200kW, production-based)
4. Shopping Mall (80kW-500kW, aggregated loads)
5. Textile Mill (100kW-250kW, cyclic production)
"""

import time
import json
import random
import threading
from kafka import KafkaProducer
from datetime import datetime
import math

# Configuration
KAFKA_BOOTSTRAP = "localhost:9092"
KAFKA_TOPIC = "telemetry-raw"

# Kafka producer
producer = KafkaProducer(
    bootstrap_servers=[KAFKA_BOOTSTRAP],
    value_serializer=lambda x: json.dumps(x).encode('utf-8')
)

print("[MULTI-METER] Starting 5-meter simulator...")
print("[INFO] All meters sending to:", KAFKA_TOPIC)

# ============================================================================
# METER 1: APARTMENT (Simple household, no AC)
# ============================================================================
def meter_apartment():
    """150W baseline -> 1500W peak"""
    meter_id = "apartment_001"
    
    while True:
        now = datetime.now()
        hour = now.hour
        
        # Simulate daily pattern (time-based)
        if 23 <= hour or hour < 6:  # Night: 200W baseline
            base_power = random.uniform(100, 200)
            voltage = 228 + random.uniform(-2, 2)
            current = base_power / voltage
        elif 6 <= hour < 8:  # Morning: cooking, shower
            base_power = random.uniform(700, 1200)
            voltage = 230 + random.uniform(-1, 1)
            current = base_power / voltage
        elif 8 <= hour < 17:  # Day: minimal (most people working)
            base_power = random.uniform(200, 500)
            voltage = 230 + random.uniform(-1, 1)
            current = base_power / voltage
        else:  # Evening: 5pm-11pm entertainment
            base_power = random.uniform(600, 1500)
            voltage = 230 + random.uniform(-1, 1)
            current = base_power / voltage
        
        # Add random noise
        power_w = base_power + random.uniform(-20, 20)
        voltage_v = voltage
        current_a = power_w / voltage_v
        frequency_hz = 50.0 + random.uniform(-0.05, 0.05)
        
        data = {
            "meter_id": meter_id,
            "timestamp": now.isoformat(),
            "power_w": round(power_w, 2),
            "voltage_v": round(voltage_v, 2),
            "current_a": round(current_a, 2),
            "frequency_hz": round(frequency_hz, 3)
        }
        
        producer.send(KAFKA_TOPIC, value=data)
        print(f"[APT] {power_w:.0f}W | V:{voltage_v:.1f}V | F:{frequency_hz:.2f}Hz")
        
        time.sleep(1)

# ============================================================================
# METER 2: SUBURBAN HOME (Typical household with AC/heating)
# ============================================================================
def meter_suburban():
    """300W baseline -> 4500W peak (seasonal variation)"""
    meter_id = "suburban_home_001"
    import datetime as dt
    
    while True:
        now = datetime.now()
        hour = now.hour
        month = now.month
        
        # Seasonal multiplier (winter=heating, summer=AC)
        if month in [12, 1, 2]:  # Winter
            seasonal = 1.5  # 50% more power for heating
        elif month in [6, 7, 8]:  # Summer
            seasonal = 1.2  # 20% more power for AC
        else:
            seasonal = 1.0  # Spring/Fall
        
        # Daily pattern
        if 23 <= hour or hour < 6:  # Night
            base_power = 200 * seasonal
        elif 6 <= hour < 8:  # Morning
            base_power = 800 * seasonal + random.uniform(0, 500)  # AC/heat on
        elif 8 <= hour < 17:  # Day
            base_power = 400 * seasonal
        elif 17 <= hour < 22:  # Evening
            base_power = 1500 * seasonal + random.uniform(0, 1000)  # Cooking + AC
        else:  # Night wind down
            base_power = 400 * seasonal
        
        # Add noise
        power_w = base_power + random.uniform(-50, 50)
        voltage_v = 230 + random.uniform(-2, 2)
        current_a = power_w / voltage_v
        frequency_hz = 50.0 + random.uniform(-0.05, 0.05)
        
        data = {
            "meter_id": meter_id,
            "timestamp": now.isoformat(),
            "power_w": round(power_w, 2),
            "voltage_v": round(voltage_v, 2),
            "current_a": round(current_a, 2),
            "frequency_hz": round(frequency_hz, 3)
        }
        
        producer.send(KAFKA_TOPIC, value=data)
        print(f"[SUB] {power_w:.0f}W | V:{voltage_v:.1f}V | I:{current_a:.1f}A")
        
        time.sleep(1)

# ============================================================================
# METER 3: AUTOMOBILE ASSEMBLY FACTORY (Production-based)
# ============================================================================
def meter_automobile():
    """50kW idle -> 200kW peak during production"""
    meter_id = "auto_factory_001"
    
    production_on = False
    production_start_time = None
    
    while True:
        now = datetime.now()
        hour = now.hour
        minute = now.minute
        
        # Factory operates 8am-8pm (2 shifts), off nights
        is_shift_time = 8 <= hour < 20
        
        if is_shift_time:
            # 80% chance production is running
            if random.random() < 0.8:
                production_on = True
                if production_start_time is None:
                    production_start_time = now
                
                # Simulate production cycle: 30-180 min runs
                elapsed = (now - production_start_time).total_seconds() / 60
                if elapsed > random.uniform(30, 180):
                    production_on = False
                    production_start_time = None
        else:
            # Night: Factory off
            production_on = False
            production_start_time = None
        
        if production_on:
            # Production running: 120-200kW
            base_power = random.uniform(120000, 200000)  # Robots, welding, conveyor
            # Occasional fault simulation (5% chance)
            if random.random() < 0.95:
                power_w = base_power
            else:
                # Simulate equipment degradation
                power_w = base_power * random.uniform(0.7, 0.85)  # 15-30% power drop
        else:
            # Idle: skeleton crew, minimal systems
            power_w = random.uniform(50000, 80000)
        
        voltage_v = 230 + random.uniform(-2, 2)
        current_a = power_w / voltage_v
        frequency_hz = 50.0 + random.uniform(-0.1, 0.1)
        
        data = {
            "meter_id": meter_id,
            "timestamp": now.isoformat(),
            "power_w": round(power_w, 2),
            "voltage_v": round(voltage_v, 2),
            "current_a": round(current_a, 2),
            "frequency_hz": round(frequency_hz, 3)
        }
        
        producer.send(KAFKA_TOPIC, value=data)
        status = "[RUNNING]" if production_on else "[IDLE]"
        print(f"[AUTO] {status} {power_w/1000:.1f}kW | I:{current_a:.1f}A")
        
        time.sleep(2)  # 2 sec interval (slower than household)

# ============================================================================
# METER 4: SHOPPING MALL (Aggregated loads - 50+ stores + HVAC)
# ============================================================================
def meter_shopping_mall():
    """80kW baseline -> 500kW peak (weather-dependent)"""
    meter_id = "shopping_mall_001"
    
    while True:
        now = datetime.now()
        hour = now.hour
        
        # Mall hours: 10am-10pm
        if 10 <= hour < 22:
            # Operating hours: stores open
            base_power = random.uniform(300000, 500000)  # All stores + AC
            
            # Peak hours: 12pm-2pm, 5pm-8pm
            if (12 <= hour < 14) or (17 <= hour < 20):
                base_power *= 1.2  # 20% more during peak
        else:
            # Closed: minimal HVAC, cleaning crew
            base_power = random.uniform(80000, 120000)
        
        # Add noise
        power_w = base_power + random.uniform(-20000, 20000)
        voltage_v = 230 + random.uniform(-3, 3)
        current_a = power_w / voltage_v
        frequency_hz = 50.0 + random.uniform(-0.1, 0.1)
        
        data = {
            "meter_id": meter_id,
            "timestamp": now.isoformat(),
            "power_w": round(power_w, 2),
            "voltage_v": round(voltage_v, 2),
            "current_a": round(current_a, 2),
            "frequency_hz": round(frequency_hz, 3)
        }
        
        producer.send(KAFKA_TOPIC, value=data)
        print(f"[MALL] {power_w/1000:.1f}kW | V:{voltage_v:.1f}V | I:{current_a:.1f}A")
        
        time.sleep(3)  # 3 sec interval (aggregated data slower)

# ============================================================================
# METER 5: TEXTILE/FABRIC MILL (Cyclic production)
# ============================================================================
def meter_textile():
    """100kW baseline -> 250kW peak (cyclic patterns)"""
    meter_id = "textile_mill_001"
    
    cycle_count = 0
    cycle_phase = "OFF"  # OFF, RAMP_UP, RUNNING, RAMP_DOWN
    cycle_timer = 0
    
    while True:
        now = datetime.now()
        hour = now.hour
        
        # Mill operates during day shift: 8am-8pm
        is_shift = 8 <= hour < 20
        
        if not is_shift:
            # Off shift
            power_w = random.uniform(5000, 10000)
            cycle_phase = "OFF"
        else:
            # During shift: simulate production cycle
            cycle_timer += 1
            
            # Cycle: 2 min ramp up, 8 min running, 1 min ramp down, 1 min off
            if cycle_timer < 2:  # Ramp up (2 min)
                power_w = random.uniform(100000, 150000)
                cycle_phase = "RAMP_UP"
            elif cycle_timer < 10:  # Running (8 min)
                power_w = random.uniform(200000, 250000)
                cycle_phase = "RUNNING"
                
                # Occasional degradation (bearing wear): 2% chance
                if random.random() < 0.02:
                    power_w *= 0.95  # Slight power drop (bearing friction)
            elif cycle_timer < 11:  # Ramp down (1 min)
                power_w = random.uniform(100000, 150000)
                cycle_phase = "RAMP_DOWN"
            else:  # Off (1 min)
                power_w = random.uniform(50000, 80000)
                cycle_phase = "OFF"
                cycle_timer = 0  # Reset cycle
        
        voltage_v = 230 + random.uniform(-2, 2)
        current_a = power_w / voltage_v
        frequency_hz = 50.0 + random.uniform(-0.05, 0.05)
        
        data = {
            "meter_id": meter_id,
            "timestamp": now.isoformat(),
            "power_w": round(power_w, 2),
            "voltage_v": round(voltage_v, 2),
            "current_a": round(current_a, 2),
            "frequency_hz": round(frequency_hz, 3)
        }
        
        producer.send(KAFKA_TOPIC, value=data)
        print(f"[TEX] {cycle_phase:8} {power_w/1000:.1f}kW | I:{current_a:.1f}A")
        
        time.sleep(1)

# ============================================================================
# MAIN: Start all 5 meters in parallel threads
# ============================================================================

threads = [
    threading.Thread(target=meter_apartment, daemon=True),
    threading.Thread(target=meter_suburban, daemon=True),
    threading.Thread(target=meter_automobile, daemon=True),
    threading.Thread(target=meter_shopping_mall, daemon=True),
    threading.Thread(target=meter_textile, daemon=True),
]

print("\n[START] Launching 5 meters...")
for i, thread in enumerate(threads, 1):
    thread.start()
    print(f"[METER {i}] Started")

print("\n[ALL METERS] Running. Press Ctrl+C to stop.\n")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n[STOP] Shutting down...")
    producer.close()
    print("[DONE]")
