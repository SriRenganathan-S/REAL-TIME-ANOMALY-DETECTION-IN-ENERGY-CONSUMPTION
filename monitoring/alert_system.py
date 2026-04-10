import json
import time
from datetime import datetime, timedelta
from kafka import KafkaConsumer
from twilio.rest import Client
from cassandra.cluster import Cluster
from collections import defaultdict

# ==========================================
# 🔧 CONFIGURATION
# ==========================================
TWILIO_DISABLED = False 

# 🚨 THRESHOLDS - Power Based
DANGER_THRESHOLD = 5000   # 🔴 Voice Call
WARNING_THRESHOLD = 3000  # 🟡 SMS Message

# 🎯 ANOMALY SCORE THRESHOLDS - NEW PHASE 4
CRITICAL_ANOMALY_SCORE = 0.85  # 🔴 CRITICAL
WARNING_ANOMALY_SCORE = 0.70   # 🟡 WARNING

# ⏱️ ALERT COOLDOWN (per meter)
ALERT_COOLDOWN_MINUTES = 5

# Credentials
ACCOUNT_SID = 'AC62a66ce4e128af99857bfa8e7f07e3eb'
AUTH_TOKEN = '07f410e52a7701cc595bc2739a59bc37'
TWILIO_PHONE = '+18123125108'
MY_PHONE = '+917418921860' 

client = Client(ACCOUNT_SID, AUTH_TOKEN)

# ==========================================
# 📊 PHASE 4 - ALERT STATE TRACKING
# ==========================================
alert_history = defaultdict(list)
last_alert_time = defaultdict(lambda: None)
meters_seen = set()

# Cassandra for alert logging
try:
    cassandra_cluster = Cluster(['127.0.0.1'])
    cassandra_session = cassandra_cluster.connect('energy_db')
    CASSANDRA_ENABLED = True
    print("✅ Cassandra connected for alert logging")
except:
    CASSANDRA_ENABLED = False
    print("⚠️  Cassandra unavailable - alerts not logged to DB")

# ==========================================

print("🔌 Twilio alerts ENABLED 🚀")
print(f"📊 Monitoring: Warning > {WARNING_THRESHOLD}W | Danger > {DANGER_THRESHOLD}W")
print(f"🎯 Anomaly Score Alerts: CRITICAL > {CRITICAL_ANOMALY_SCORE} | WARNING > {WARNING_ANOMALY_SCORE}\n")

# --- STARTUP VERIFICATION CALL ---
if not TWILIO_DISABLED:
    try:
        print("📞 Initiating System Startup Verification Call...")
        startup_call = client.calls.create(
            twiml='<Response><Say>System Boot Sequence Complete. Your Real Time Energy Anomaly Detection pipeline is now fully online.</Say></Response>',
            to=MY_PHONE,
            from_=TWILIO_PHONE
        )
        print(f"✅ Startup Call Placed Successfully: {startup_call.sid}\n")
    except Exception as e:
        print(f"❌ Startup Call Failed: {e}\n")

# ==========================================
# 🚨 PHASE 4 - ANOMALY ALERT FUNCTIONS
# ==========================================

def log_alert_to_cassandra(meter_id, anomaly_score, power_w, alert_level, notification_type):
    """Log alert to Cassandra for audit trail"""
    if not CASSANDRA_ENABLED:
        return
    
    try:
        query = """
        INSERT INTO alerts 
        (meter_id, timestamp, anomaly_score, power_w, alert_level, notification_type)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        cassandra_session.execute(query, (
            meter_id,
            datetime.now(),
            float(anomaly_score),
            float(power_w),
            alert_level,
            notification_type
        ))
    except Exception as e:
        print(f"⚠️  Cassandra log failed: {e}")

def trigger_anomaly_alert(meter_id, anomaly_score, power_w, alert_level):
    """🎯 PHASE 4 - Anomaly-based alert handler"""
    now = datetime.now()
    
    # Check per-meter cooldown
    last_alert = last_alert_time.get(meter_id)
    if last_alert:
        time_since = (now - last_alert).total_seconds() / 60
        if time_since < ALERT_COOLDOWN_MINUTES:
            return
    
    # Update last alert time
    last_alert_time[meter_id] = now
    
    # Log to Cassandra
    log_alert_to_cassandra(meter_id, anomaly_score, power_w, alert_level, "ANOMALY")
    
    print(f"\n🚨 {alert_level} ANOMALY DETECTED!")
    print(f"   Meter: {meter_id}")
    print(f"   Score: {anomaly_score:.4f} (threshold: {CRITICAL_ANOMALY_SCORE if alert_level == 'CRITICAL' else WARNING_ANOMALY_SCORE})")
    print(f"   Power: {power_w:.2f}W")
    print(f"   Time: {now.strftime('%H:%M:%S')}")
    
    # Send notifications based on severity
    if alert_level == "CRITICAL" and not TWILIO_DISABLED:
        try:
            call = client.calls.create(
                twiml=f'<Response><Say>Critical Anomaly on {meter_id}. Anomaly score {anomaly_score:.4f}. Power {power_w:.0f} watts.</Say></Response>',
                to=MY_PHONE,
                from_=TWILIO_PHONE
            )
            print(f"   ☎️ Call Placed: {call.sid}")
        except Exception as e:
            print(f"   ❌ Call Failed: {e}")
    
    elif alert_level == "WARNING" and not TWILIO_DISABLED:
        try:
            message = client.messages.create(
                body=f"⚠️ Anomaly Warning on {meter_id}: Score {anomaly_score:.4f}, Power {power_w:.0f}W",
                from_=TWILIO_PHONE,
                to=MY_PHONE
            )
            print(f"   📩 SMS Sent: {message.sid}")
        except Exception as e:
            print(f"   ❌ SMS Failed: {e}")

consumer = KafkaConsumer(
    'telemetry-processed',
    bootstrap_servers='localhost:9092',
    value_deserializer=lambda x: json.loads(x.decode('utf-8')),
    auto_offset_reset='latest',
    group_id='alert-system-phase4'
)

print("✅ Connected to Kafka: telemetry-processed")
print(f"📊 Alert Cooldown: {ALERT_COOLDOWN_MINUTES} minutes per meter\n")

def trigger_voice_call(current_power):
    """🔴 CRITICAL: Phone Call [LEGACY - Use trigger_anomaly_alert instead]"""
    print(f"☎️ DANGER! Initiating Call to {MY_PHONE}...")
    try:
        call = client.calls.create(
            twiml=f'<Response><Say>Critical Alert! Power usage is {current_power} Watts.</Say></Response>',
            to=MY_PHONE,
            from_=TWILIO_PHONE
        )
        print(f"✅ Call Placed. SID: {call.sid}")
    except Exception as e:
        print(f"❌ Call Failed: {e}")

def trigger_sms_notification(current_power):
    """🟡 WARNING: SMS Message [LEGACY - Use trigger_anomaly_alert instead]"""
    print(f"📩 WARNING! Sending SMS to {MY_PHONE}...")
    try:
        message = client.messages.create(
            body=f"⚠️ [Energy Alert] Warning: High power consumption detected at {current_power}W.",
            from_=TWILIO_PHONE,
            to=MY_PHONE
        )
        print(f"✅ SMS Sent. SID: {message.sid}")
    except Exception as e:
        print(f"❌ SMS Failed: {e}")

# PHASE 4: New alert functions above

# --- MAIN WATCH LOOP ---
processed_count = 0
anomaly_alerts_count = 0
power_alerts_count = 0

try:
    for message in consumer:
        data = message.value
        meter_id = data.get('meter_id', 'unknown')
        power = data.get('power_w', 0)
        anomaly_score = data.get('anomaly_score', 0)
        
        processed_count += 1
        
        # Track meters
        if meter_id not in meters_seen:
            meters_seen.add(meter_id)
            print(f"📍 New meter detected: {meter_id}")
        
        # === PHASE 4 - ANOMALY-BASED ALERTS (PRIMARY) ===
        if anomaly_score > 0:
            if anomaly_score >= CRITICAL_ANOMALY_SCORE:
                anomaly_alerts_count += 1
                trigger_anomaly_alert(meter_id, anomaly_score, power, "CRITICAL")
                
            elif anomaly_score >= WARNING_ANOMALY_SCORE:
                anomaly_alerts_count += 1
                trigger_anomaly_alert(meter_id, anomaly_score, power, "WARNING")
        
        # === LEGACY - POWER-BASED ALERTS (FALLBACK) ===
        else:
            # 1. 🔴 DANGER ZONE (> 5000W)
            if power > DANGER_THRESHOLD:
                power_alerts_count += 1
                print(f"\n🚨 [CRITICAL-POWER] {meter_id}: {power}W")
                
                if not TWILIO_DISABLED:
                    try:
                        call = client.calls.create(
                            twiml=f'<Response><Say>Critical! Power usage is {power} Watts on {meter_id}.</Say></Response>',
                            to=MY_PHONE,
                            from_=TWILIO_PHONE
                        )
                        print(f"   ☎️ Call Placed: {call.sid}")
                        log_alert_to_cassandra(meter_id, 0, power, "CRITICAL", "POWER")
                    except Exception as e:
                        print(f"   ❌ Call Failed: {e}")

                # GLOBAL COOLDOWN: 60 seconds
                print("⏳ Cooldown: Pausing for 60 seconds...")
                time.sleep(60)

            # 2. 🟡 WARNING ZONE (> 3000W)
            elif power > WARNING_THRESHOLD:
                power_alerts_count += 1
                print(f"\n⚠️ [WARNING-POWER] {meter_id}: {power}W")
                
                if not TWILIO_DISABLED:
                    try:
                        message = client.messages.create(
                            body=f"⚠️ [Energy Alert] {meter_id}: High power consumption {power}W.",
                            from_=TWILIO_PHONE,
                            to=MY_PHONE
                        )
                        print(f"   📩 SMS Sent: {message.sid}")
                        log_alert_to_cassandra(meter_id, 0, power, "WARNING", "POWER")
                    except Exception as e:
                        print(f"   ❌ SMS Failed: {e}")

                # GLOBAL COOLDOWN: 30 seconds
                print("⏳ Cooldown: Pausing for 30 seconds...")
                time.sleep(30)
        
        # Status update every 100 messages
        if processed_count % 100 == 0:
            print(f"\n📊 Status: Processed={processed_count} | Anomaly Alerts={anomaly_alerts_count} | Power Alerts={power_alerts_count} | Meters={len(meters_seen)}")
            
except KeyboardInterrupt:
    print(f"\n\n✅ Alert System Stopped.")
    print(f"📈 Final Stats: Processed={processed_count} | Anomaly Alerts={anomaly_alerts_count} | Power Alerts={power_alerts_count}")

finally:
    consumer.close()
    if CASSANDRA_ENABLED:
        cassandra_session.shutdown()