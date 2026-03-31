"""
SPARK BRAIN - SMART SILENCE VERSION
Features:
1. 2-Minute Learning Silence (No Cold Start Panic)
2. 60-Second Alert Cool-Down (No Spam Calls)
3. 50W Noise Gate (No Phone Charger Alerts)
"""
import os
import sys
import json
import time
from datetime import datetime

# --- 1. GLOBAL CONFIGURATION ---
TWILIO_SID = os.getenv("TWILIO_SID", "AC_DUMMY").strip()
TWILIO_TOKEN = os.getenv("TWILIO_TOKEN", "dummy_token").strip()
FROM_NUMBER = os.getenv("FROM_NUMBER", "+15550000000").strip()
TO_NUMBER = os.getenv("TO_NUMBER", "+919876543210").strip()
KAFKA_TOPIC_RAW = "telemetry-raw"
KAFKA_TOPIC_PROCESSED = "telemetry-processed"
KAFKA_TOPIC_ANOMALIES = "anomalies-detected"
KAFKA_TOPIC_ALERTS = "alerts-critical"

# --- SCORE NORMALIZATION FUNCTION ---
def normalize_score(raw_score):
    """Normalize anomaly score to 0-1 range using sigmoid function"""
    import math
    try:
        # Sigmoid normalization: ensures score is always between 0-1
        normalized = 1.0 / (1.0 + math.exp(-float(raw_score)))
        return float(max(0.0, min(1.0, normalized)))
    except:
        return 0.0

# --- 2. ANNOYANCE CONTROL SETTINGS ---
LEARNING_LIMIT = 100 
MIN_POWER_THRESHOLD = 50.0 
ALERT_COOLDOWN = 60 

IS_WINDOWS = sys.platform == 'win32'
print(f"[DEBUG] Platform: {sys.platform}, IS_WINDOWS: {IS_WINDOWS}")

if IS_WINDOWS:
    print("⚠️  Windows detected - using adaptive Python implementation")
    
    from kafka import KafkaConsumer
    from cassandra.cluster import Cluster
    from river import anomaly, compose, preprocessing
    from twilio.rest import Client
    
    KAFKA_BOOTSTRAP = "localhost:9092"
    CASSANDRA_HOSTS = ["127.0.0.1"]
    
    try:
        client = Client(TWILIO_SID, TWILIO_TOKEN)
    except:
        pass
    
    try:
        consumer = KafkaConsumer(
            KAFKA_TOPIC_RAW,
            bootstrap_servers=KAFKA_BOOTSTRAP.split(","),
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            auto_offset_reset='latest', 
            group_id=None
        )
        print(f"✅ Connected to Kafka: {KAFKA_BOOTSTRAP}, Topic: {KAFKA_TOPIC_RAW}")
    except Exception as e:
        print(f"❌ Kafka connection error: {e}")
        sys.exit(1)
    
    try:
        cluster = Cluster(CASSANDRA_HOSTS)
        session = cluster.connect()
        session.set_keyspace('energy_db')
        print(f"✅ Connected to Cassandra: {CASSANDRA_HOSTS}")
    except Exception as e:
        print(f"❌ Cassandra connection error: {e}")
        sys.exit(1)
    
    # --- MULTI-METER SUPPORT ---
    meter_models = {}
    meter_learning_counts = {}
    meter_last_alerts = {}
    
    def get_or_create_model(meter_id):
        """Get existing model or create new one for meter"""
        if meter_id not in meter_models:
            meter_models[meter_id] = compose.Pipeline(
                preprocessing.StandardScaler(),
                anomaly.HalfSpaceTrees(n_trees=50, height=8, window_size=50, seed=42)
            )
            meter_learning_counts[meter_id] = 0
            meter_last_alerts[meter_id] = 0
            print(f"[MULTI-METER] Model created for {meter_id}")
        return meter_models[meter_id]
    
    count = 0
    last_alert_time = 0
    last_heartbeat_time = 0
    heartbeat_interval = 5 
    
    print(f"🧠 Brain Active! Multi-Meter Learning Mode...")
    
    try:
        for message in consumer:
            data = message.value
            meter_id = str(data.get('meter_id', 'unknown'))
            power = float(data['power_w'])
            voltage = float(data.get('voltage_v', 230.0))
            current = float(data.get('current_a', 0.0))
            freq = float(data.get('frequency_hz', 50.0))
            
            timestamp_obj = datetime.now()
            features = {'power': power, 'voltage': voltage, 'current': current}
            
            # Get model for this meter
            model = get_or_create_model(meter_id)
            meter_learning_counts[meter_id] += 1
            learning_count = meter_learning_counts[meter_id]
            count += 1
        
            if learning_count < LEARNING_LIMIT:
                status = "Learning"
                score = 0.0
                model.learn_one(features)
                print(f"🎓 [{meter_id}] Learning... ({learning_count}/{LEARNING_LIMIT}) Power: {power}W")
                
            elif power < MIN_POWER_THRESHOLD:
                status = "Safe (Idle)"
                score = 0.0
                model.learn_one(features)
                print(f"💤 [{meter_id}] Idle: {power}W")
                
            else:
                raw_score = model.score_one(features)
                score = normalize_score(raw_score)  # Normalize to 0-1 range
                model.learn_one(features)
                
                if score > 0.7:
                    status = "CRITICAL"
                    time_since_last_alert = time.time() - meter_last_alerts[meter_id]
                    if time_since_last_alert > ALERT_COOLDOWN:
                        print(f"🚨 [{meter_id}] DANGER! Sending Alert... (Score: {score:.2f})")
                        if "DUMMY" not in TWILIO_SID:
                            try:
                                client.messages.create(body=f"🚨 [{meter_id}] Energy Alert: {power}W detected!", from_=FROM_NUMBER, to=TO_NUMBER)
                                meter_last_alerts[meter_id] = time.time()
                            except: print("❌ Twilio Error")
                        else:
                            print("📲 (Simulated Call Sent)")
                            meter_last_alerts[meter_id] = time.time()
                else:
                    status = "Normal"
                    print(f"✅ [{meter_id}] Safe: {power}W (Score: {score:.2f})")
    
            # CRITICAL: Use meter_id from data
            query = """
                INSERT INTO meter_readings (
                    meter_id, timestamp, power_w, anomaly_score, status, voltage_v, current_a, frequency_hz
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            session.execute(query, (meter_id, timestamp_obj, float(power), float(score), status, float(voltage), float(current), float(freq)))
            
            current_time = time.time()
            if current_time - last_heartbeat_time > heartbeat_interval:
                heartbeat_query = "INSERT INTO system_heartbeat (processor_id, timestamp, status, last_update) VALUES (%s, %s, %s, %s)"
                session.execute(heartbeat_query, ("spark_brain_processor", timestamp_obj, "ALIVE", timestamp_obj))
                print(f"❤️  Heartbeat recorded")
                last_heartbeat_time = current_time
    
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        cluster.shutdown()

else:
    # --- LINUX / DOCKER MODE - PYSPARK STRUCTURED STREAMING ---
    print("🐧 Linux detected - Starting PySpark Structured Streaming")
    
    from pyspark.sql import SparkSession
    from pyspark.sql.functions import col, from_json, window, when, udf, current_timestamp, to_json, struct
    from pyspark.sql.types import StructType, StructField, StringType, DoubleType, TimestampType
    from river import anomaly, compose, preprocessing
    from cassandra.cluster import Cluster
    from cassandra.query import BatchStatement
    from twilio.rest import Client
    import uuid
    import pickle
    import base64
    
    # --- Initialize Spark Session ---
    try:
        spark = SparkSession.builder \
            .appName("EnergyAnomalyDetection") \
            .config("spark.cassandra.connection.host", os.getenv("CASSANDRA_HOST", "172.25.0.10")) \
            .config("spark.cassandra.connection.port", "9042") \
            .config("spark.cassandra.auth.username", "cassandra") \
            .config("spark.cassandra.auth.password", "cassandra") \
            .config("spark.sql.streaming.checkpointLocation", "/tmp/spark_checkpoint") \
            .getOrCreate()
        
        spark.sparkContext.setLogLevel("WARN")
        print(f"✅ Spark Session Created")
    except Exception as e:
        print(f"❌ Spark Session Error: {e}")
        sys.exit(1)
    
    # --- Schema for Kafka Messages ---
    schema = StructType([
        StructField("meter_id", StringType()),
        StructField("power_w", DoubleType()),
        StructField("voltage_v", DoubleType()),
        StructField("current_a", DoubleType()),
        StructField("frequency_hz", DoubleType()),
        StructField("status_label", StringType())
    ])
    
    # --- Read from Kafka ---
    try:
        kafka_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:29092")
        df_stream = spark \
            .readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", kafka_servers) \
            .option("subscribe", KAFKA_TOPIC_RAW) \
            .option("startingOffsets", "latest") \
            .load()
        
        print(f"✅ Connected to Kafka: {kafka_servers}, Reading from topic: {KAFKA_TOPIC_RAW}")
    except Exception as e:
        print(f"❌ Kafka Connection Error: {e}")
        sys.exit(1)
    
    # --- Initialize Cassandra Connection for Model State ---
    try:
        cassandra_host = os.getenv("CASSANDRA_HOST", "172.25.0.10")
        cluster = Cluster([cassandra_host])
        session = cluster.connect()
        session.set_keyspace('energy_db')
        print(f"✅ Connected to Cassandra: {cassandra_host}")
    except Exception as e:
        print(f"❌ Cassandra Connection Error: {e}")
        sys.exit(1)
    
    # --- Initialize Twilio ---
    try:
        client = Client(TWILIO_SID, TWILIO_TOKEN)
    except:
        pass
    
    # --- Initialize Per-Meter River ML Models (Multi-Meter Support) ---
    meter_models = {}  # Dictionary: meter_id -> model
    meter_learning_counts = {}  # Dictionary: meter_id -> learning_count
    meter_last_alerts = {}  # Dictionary: meter_id -> last_alert_time
    
    def get_or_create_model(meter_id):
        """Get existing model or create new one for meter"""
        if meter_id not in meter_models:
            meter_models[meter_id] = compose.Pipeline(
                preprocessing.StandardScaler(),
                anomaly.HalfSpaceTrees(n_trees=50, height=8, window_size=50, seed=42)
            )
            meter_learning_counts[meter_id] = 0
            meter_last_alerts[meter_id] = 0
            print(f"[MULTI-METER] Model created for {meter_id}")
        return meter_models[meter_id]
    
    last_heartbeat_time = [0]
    
    # --- 2-Tier Risk Classification Function ---
    def classify_anomaly(score, power, voltage, current, frequency):
        """
        Tier 1: Anomaly Score (0.0-1.0)
        Tier 2: Hard Power Thresholds (fault detection)
        Returns: (risk_level, fault_type)
        """
        # Tier 2: Fault Detection Rules (Paper Table III)
        if power < 100 and power > 0:  # Usually <500W, now <100W
            return "CRITICAL", "SHORT_CIRCUIT_SUSPECTED"
        if voltage > 250 or voltage < 200:
            return "ALERT", "GRID_VOLTAGE_OVERVOLTAGE"
        if frequency < 49.0 or frequency > 50.5:
            return "WARNING", "FREQUENCY_DEVIATION"
        if current > 30:  # Extreme current
            return "CRITICAL", "OVERCURRENT_DETECTED"
        
        # Tier 1: Anomaly Score Based
        if score > 0.9:
            return "CRITICAL", "ANOMALY_CRITICAL"
        elif score > 0.7:
            return "ALERT", "ANOMALY_ALERT"
        elif score > 0.5:
            return "WARNING", "ANOMALY_WARNING"
        else:
            return "NORMAL", "OK"
    
    # Parse Kafka Messages ---
    df_parsed = df_stream.select(
        from_json(col("value").cast("string"), schema).alias("data"),
        col("timestamp").alias("kafka_timestamp")
    ).select("data.*", "kafka_timestamp")
    
    # --- Anomaly Detection UDF (Per-Meter Model) ---
    def detect_anomaly(meter_id, power, voltage, current, frequency):
        """Apply River ML model (independent per meter)"""
        try:
            model = get_or_create_model(meter_id)
            count_learning = meter_learning_counts[meter_id]
            features = {'power': float(power), 'voltage': float(voltage), 'current': float(current)}
            
            meter_learning_counts[meter_id] += 1
            
            if count_learning < LEARNING_LIMIT:
                score = 0.0
                model.learn_one(features)
            elif power < MIN_POWER_THRESHOLD:
                score = 0.0
                model.learn_one(features)
            else:
                raw_score = float(model.score_one(features))
                score = normalize_score(raw_score)  # Normalize to 0-1 range
                model.learn_one(features)
            
            # Apply 2-tier classification
            risk_level, fault_type = classify_anomaly(score, power, voltage, current, frequency)
            
            return float(score), risk_level, fault_type
        except Exception as e:
            print(f"❌ Model Error for {meter_id}: {e}")
            return 0.0, "ERROR", "DETECTION_FAILED"
    
    # Register detection UDF - returns (score, risk_level, fault_type)
    detect_udf = udf(
        lambda mid, pw, vv, ca, fh: detect_anomaly(mid, pw, vv, ca, fh) if mid else (0.0, "ERROR", "NO_METER"),
        "struct<score: double, risk_level: string, fault_type: string>"
    )
    
    # --- Apply Anomaly Detection (Per-Meter) ---
    df_with_anomaly = df_parsed.withColumn(
        "anomaly_result",
        detect_udf(col("meter_id"), col("power_w"), col("voltage_v"), col("current_a"), col("frequency_hz"))
    ).select(
        col("meter_id"),
        col("power_w"),
        col("voltage_v"),
        col("current_a"),
        col("frequency_hz"),
        col("status_label"),
        col("kafka_timestamp").alias("timestamp"),
        col("anomaly_result.score").alias("anomaly_score"),
        col("anomaly_result.risk_level").alias("risk_level"),
        col("anomaly_result.fault_type").alias("fault_type")
    )
    
    # --- Write to Cassandra + Send Alerts + Write to Topics (Multi-Meter) ---
    def write_to_cassandra(batch_df, batch_id):
        """Write batch to Cassandra, route to Kafka topics, save model state (per-meter)"""
        try:
            for row in batch_df.collect():
                meter_id = row['meter_id']
                timestamp = row['timestamp']
                power = row['power_w']
                anomaly_score = row['anomaly_score']
                risk_level = row['risk_level']
                fault_type = row['fault_type']
                voltage = row['voltage_v']
                current = row['current_a']
                frequency = row['frequency_hz']
                
                # 1. INSERT TO CASSANDRA - meter_readings
                query = """
                    INSERT INTO meter_readings (
                        meter_id, timestamp, power_w, anomaly_score, status, voltage_v, current_a, frequency_hz
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                session.execute(query, (meter_id, timestamp, float(power), float(anomaly_score), risk_level, float(voltage), float(current), float(frequency)))
                
                # 2. SAVE PER-METER MODEL STATE every 100 readings
                if meter_id in meter_learning_counts and meter_learning_counts[meter_id] % 100 == 0:
                    try:
                        model = get_or_create_model(meter_id)
                        model_checkpoint = base64.b64encode(pickle.dumps(model)).decode('utf-8')
                        baseline_power = float(power)
                        update_model_query = """
                            UPDATE model_states SET model_checkpoint=%s, baseline_power=%s, learning_count=%s, last_updated=%s 
                            WHERE meter_id=%s
                        """
                        session.execute(update_model_query, (model_checkpoint, baseline_power, meter_learning_counts[meter_id], datetime.now(), meter_id))
                        print(f"💾 [{meter_id}] Model checkpoint saved (readings: {meter_learning_counts[meter_id]})")
                    except Exception as e:
                        print(f"❌ Model save error for {meter_id}: {e}")
                
                # 3. ROUTE TO APPROPRIATE KAFKA TOPIC
                from kafka import KafkaProducer as KP
                kafka_producer = KP(bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:29092").split(","),
                                               value_serializer=lambda x: json.dumps(x).encode('utf-8'))
                
                event_data = {
                    "meter_id": meter_id,
                    "timestamp": timestamp.isoformat() if hasattr(timestamp, 'isoformat') else str(timestamp),
                    "power_w": float(power),
                    "voltage_v": float(voltage),
                    "current_a": float(current),
                    "frequency_hz": float(frequency),
                    "anomaly_score": float(anomaly_score),
                    "risk_level": risk_level,
                    "fault_type": fault_type
                }
                
                # Write to processed topic
                kafka_producer.send(KAFKA_TOPIC_PROCESSED, value=event_data)
                
                # Write to anomalies topic if anomaly detected
                if risk_level in ["ALERT", "CRITICAL"]:
                    kafka_producer.send(KAFKA_TOPIC_ANOMALIES, value=event_data)
                
                # Send Alert if CRITICAL (Per-meter cooldown)
                if risk_level == "CRITICAL":
                    current_time = time.time()
                    meter_alert_key = f"{meter_id}_alert_time"
                    last_meter_alert = meter_last_alerts.get(meter_id, 0)
                    
                    if current_time - last_meter_alert > ALERT_COOLDOWN:
                        # Write to critical alerts topic
                        kafka_producer.send(KAFKA_TOPIC_ALERTS, value=event_data)
                        
                        print(f"🚨 [{meter_id}] CRITICAL! {fault_type}: {power}W (Score: {anomaly_score:.2f})")
                        if "DUMMY" not in TWILIO_SID:
                            try:
                                client.messages.create(
                                    body=f"🚨 CRITICAL [{meter_id}]: {fault_type} - {power}W",
                                    from_=FROM_NUMBER,
                                    to=TO_NUMBER
                                )
                                meter_last_alerts[meter_id] = current_time
                                print(f"📞 Alert SMS sent for {meter_id}")
                            except Exception as e:
                                print(f"❌ Twilio Error for {meter_id}: {e}")
                        else:
                            print(f"📲 (Simulated Alert for {meter_id})")
                            meter_last_alerts[meter_id] = current_time
                
                # Heartbeat
                current_time = time.time()
                if current_time - last_heartbeat_time[0] > 5:
                    heartbeat_query = "INSERT INTO system_heartbeat (processor_id, timestamp, status, last_update) VALUES (%s, %s, %s, %s)"
                    session.execute(heartbeat_query, ("spark_brain_processor", datetime.now(), f"ALIVE ({len(meter_models)} meters)", datetime.now()))
                    last_heartbeat_time[0] = current_time
                    print(f"❤️  Heartbeat: {len(meter_models)} meters active")
        
        except Exception as e:
            print(f"❌ Write Error: {e}")
    
    # --- Start Streaming Query ---
    try:
        query = df_with_anomaly \
            .writeStream \
            .foreachBatch(write_to_cassandra) \
            .option("checkpointLocation", "/tmp/spark_checkpoint") \
            .start()
        
        print(f"🧠 Brain Active! Processing stream from Kafka...")
        query.awaitTermination()
    
    except Exception as e:
        print(f"❌ Streaming Error: {e}")
    finally:
        session.shutdown()