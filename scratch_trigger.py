import json
import time
from kafka import KafkaProducer

print("Connecting to Kafka...")
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda x: json.dumps(x).encode('utf-8')
)

# 1. Trigger voice call (CRITICAL >= 0.85)
msg1 = {
    "meter_id": "demo_apartment_critical_003",
    "power_w": 5500,
    "anomaly_score": 0.99
}
producer.send('telemetry-processed', value=msg1)
print("Pushed CRITICAL Anomaly (Expect Voice Call)")

# 2. Trigger SMS (WARNING >= 0.70 < 0.85)
msg2 = {
    "meter_id": "demo_mall_warning_003",
    "power_w": 200000,
    "anomaly_score": 0.81
}
producer.send('telemetry-processed', value=msg2)
print("Pushed WARNING Anomaly (Expect SMS)")

producer.flush()
print("Simulated Anomalies Sent successfully!")
