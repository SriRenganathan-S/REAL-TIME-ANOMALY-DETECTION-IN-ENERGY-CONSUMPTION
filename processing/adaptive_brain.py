import json
import time
from kafka import KafkaConsumer
from cassandra.cluster import Cluster
from river import anomaly
from river import compose
from river import preprocessing

# --- CONFIGURATION ---
KAFKA_TOPIC = "energy-stream-live-v3"

# TWILIO DISABLED
TWILIO_DISABLED = True
print("🔌 Twilio DISABLED\n")

# CONNECT TO KAFKA
consumer = KafkaConsumer(
    KAFKA_TOPIC,
    bootstrap_servers=['localhost:9092'],
    value_deserializer=lambda x: json.loads(x.decode('utf-8')),
    auto_offset_reset='latest', 
    group_id=None
)

# CONNECT TO CASSANDRA
cluster = Cluster(['localhost'])
session = cluster.connect('energy_db')

# --- THE FIX: PIPELINE WITH SCALER ---
# We wrap the model so it scales the data (400 -> 0.1, 8500 -> 10.0) automatically.
model = compose.Pipeline(
    preprocessing.StandardScaler(),
    anomaly.HalfSpaceTrees(
        n_trees=50,
        height=8,
        window_size=50,
        seed=42
    )
)

LEARNING_LIMIT = 30
count = 0

print(f"🧠 AI Brain Listening on {KAFKA_TOPIC}...")

# MAIN LOOP
for message in consumer:
    data = message.value
    power = data['power_w']
    features = {'power': power}
    count += 1

    # PHASE 1: LEARN (Observation Mode)
    if count < LEARNING_LIMIT:
        status = "Learning"
        score = 0.0
        print(f"🎓 Learning Baseline... ({count}/{LEARNING_LIMIT}) - Power: {power}W")
        model.learn_one(features)

    # PHASE 2: DETECT (Active Mode)
    else:
        score = model.score_one(features)
        
        # INCREASE SENSITIVITY: 
        # With scaling, anomalies will have very high scores (close to 1.0).
        if score > 0.6: 
            status = "CRITICAL"
            print(f"🚨 DANGER! Anomaly Detected! Power: {power}W (Score: {score:.2f})")
        else:
            status = "Normal"
            print(f"✅ Safe. Power: {power}W (Score: {score:.2f})")

        model.learn_one(features)

    # SAVE TO DATABASE (Store all available meter data)
    try:
        # Try to update with all columns
        query = "INSERT INTO meter_readings (meter_id, timestamp, power_w, voltage_v, current_a, frequency_hz, power_factor, anomaly_score, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        session.execute(query, (
            data['meter_id'], 
            data['timestamp'], 
            float(data['power_w']),
            float(data['voltage_v']),
            float(data['current_a']),
            float(data['frequency_hz']),
            float(data.get('power_factor', 0.95)),
            float(score), 
            status
        ))
    except Exception as e:
        # Fallback: If columns don't exist, use basic columns
        try:
            query = "INSERT INTO meter_readings (meter_id, timestamp, power_w, anomaly_score, status) VALUES (%s, %s, %s, %s, %s)"
            session.execute(query, (data['meter_id'], data['timestamp'], float(power), float(score), status))
        except Exception as e2:
            print(f"❌ Insert failed: {e2}")