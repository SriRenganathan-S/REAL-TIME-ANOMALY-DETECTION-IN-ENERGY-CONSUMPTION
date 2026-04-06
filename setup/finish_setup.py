import requests
import json
import sys

# --- CONFIGURATION ---
GRAFANA_URL = "http://localhost:3000"
AUTH = ("admin", "admin")
HEADERS = {'Content-Type': 'application/json'}

print("\n🚀 BUILDING 'MISSION CONTROL' DASHBOARD (Spark Brain Edition)...")

# ---------------------------------------------------------
# STEP 1: GET DATASOURCE UID
# ---------------------------------------------------------
try:
    ds_res = requests.get(f"{GRAFANA_URL}/api/datasources/name/Cassandra-Fixed", auth=AUTH)
    if ds_res.status_code != 200:
        print("❌ Error: 'Cassandra-Fixed' datasource not found. Please run the connection script first.")
        sys.exit(1)
    ds_uid = ds_res.json()['uid']
    print(f"✅ Found Datasource UID: {ds_uid}")
except Exception as e:
    print(f"❌ Connection Error: {e}")
    sys.exit(1)

# ---------------------------------------------------------
# STEP 2: DEFINE THE DASHBOARD JSON
# ---------------------------------------------------------
dashboard_json = {
    "dashboard": {
        "id": None,
        "title": "⚡ Mission Control (Spark Brain)",
        "uid": "spark-brain-mission-control",
        "refresh": "1s",
        "timezone": "browser",
        "panels": [
            # --- ROW 1: STATUS & HEALTH ---
            {
                "id": 1,
                "title": "🧠 BRAIN HEARTBEAT",
                "type": "stat",
                "gridPos": {"h": 6, "w": 4, "x": 0, "y": 0},
                "datasource": {"type": "hadesarchitect-cassandra-datasource", "uid": ds_uid},
                "targets": [{
                    "rawQuery": True,
                    "query": "SELECT status FROM energy_db.system_heartbeat WHERE processor_id = 'spark_brain_processor' ORDER BY timestamp DESC LIMIT 1 ALLOW FILTERING",
                    "refId": "A"
                }],
                "fieldConfig": {
                    "defaults": {
                        "color": {"mode": "continuous-GrYlRd"},
                        "mappings": [
                            {"type": "value", "options": {"ALIVE": {"color": "green", "text": "ONLINE 🟢"}, "DEAD": {"color": "red", "text": "OFFLINE 🔴"}}}
                        ]
                    }
                }
            },
            {
                "id": 2,
                "title": "SYSTEM STATUS",
                "type": "stat",
                "gridPos": {"h": 6, "w": 8, "x": 4, "y": 0},
                "datasource": {"type": "hadesarchitect-cassandra-datasource", "uid": ds_uid},
                "targets": [{
                    "rawQuery": True,
                    "query": "SELECT status FROM energy_db.meter_readings WHERE meter_id = 'Universal_Meter_001' ORDER BY timestamp DESC LIMIT 1 ALLOW FILTERING",
                    "refId": "A"
                }],
                "fieldConfig": {
                    "defaults": {
                        "mappings": [
                            {"type": "value", "options": {"Normal": {"color": "green"}, "CRITICAL": {"color": "red"}, "Safe (Idle)": {"color": "blue"}, "Learning": {"color": "yellow"}}}
                        ],
                        "color": {"mode": "thresholds"}
                    }
                }
            },
            {
                "id": 3,
                "title": "LIVE POWER (Watts)",
                "type": "gauge",
                "gridPos": {"h": 6, "w": 12, "x": 12, "y": 0},
                "datasource": {"type": "hadesarchitect-cassandra-datasource", "uid": ds_uid},
                "targets": [{
                    "rawQuery": True,
                    "query": "SELECT power_w FROM energy_db.meter_readings WHERE meter_id = 'Universal_Meter_001' ORDER BY timestamp DESC LIMIT 1 ALLOW FILTERING",
                    "refId": "A"
                }],
                "fieldConfig": {
                    "defaults": {
                        "min": 0, "max": 6000,
                        "thresholds": {
                            "mode": "absolute", 
                            "steps": [{"color": "green", "value": None}, {"color": "#EAB839", "value": 3000}, {"color": "red", "value": 5000}]
                        }
                    }
                }
            },

            # --- ROW 2: REAL-TIME GRAPHS ---
            {
                "id": 4,
                "title": "📈 POWER CONSUMPTION TREND",
                "type": "timeseries",
                "gridPos": {"h": 10, "w": 12, "x": 0, "y": 6},
                "datasource": {"type": "hadesarchitect-cassandra-datasource", "uid": ds_uid},
                "targets": [{
                    "rawQuery": True,
                    "query": "SELECT timestamp, power_w FROM energy_db.meter_readings WHERE meter_id = 'Universal_Meter_001' LIMIT 500 ALLOW FILTERING",
                    "refId": "A"
                }],
                "fieldConfig": {
                    "defaults": {
                        "custom": {"drawStyle": "line", "lineInterpolation": "smooth", "fillOpacity": 20, "lineWidth": 2},
                        "unit": "watt",
                        "color": {"mode": "fixed", "fixedColor": "green"}
                    }
                }
            },
            {
                "id": 5,
                "title": "🤖 AI ANOMALY SCORE (0.0 - 1.0)",
                "type": "timeseries",
                "gridPos": {"h": 10, "w": 12, "x": 12, "y": 6},
                "datasource": {"type": "hadesarchitect-cassandra-datasource", "uid": ds_uid},
                "targets": [{
                    "rawQuery": True,
                    "query": "SELECT timestamp, anomaly_score FROM energy_db.meter_readings WHERE meter_id = 'Universal_Meter_001' LIMIT 500 ALLOW FILTERING",
                    "refId": "A"
                }],
                "fieldConfig": {
                    "defaults": {
                        "custom": {"drawStyle": "bars", "fillOpacity": 80},
                        "min": 0, "max": 1,
                        "thresholds": {
                            "mode": "absolute", 
                            "steps": [{"color": "green", "value": None}, {"color": "red", "value": 0.7}]
                        }
                    }
                }
            },

            # --- ROW 3: METRICS & LOGS ---
            {
                "id": 6,
                "title": "VOLTAGE (V)",
                "type": "stat",
                "gridPos": {"h": 6, "w": 6, "x": 0, "y": 16},
                "datasource": {"type": "hadesarchitect-cassandra-datasource", "uid": ds_uid},
                "targets": [{
                    "rawQuery": True,
                    "query": "SELECT voltage_v FROM energy_db.meter_readings WHERE meter_id = 'Universal_Meter_001' ORDER BY timestamp DESC LIMIT 1 ALLOW FILTERING",
                    "refId": "A"
                }],
                "fieldConfig": {"defaults": {"min": 210, "max": 250, "unit": "volt", "color": {"mode": "thresholds"}}}
            },
            {
                "id": 7,
                "title": "CURRENT (A)",
                "type": "stat",
                "gridPos": {"h": 6, "w": 6, "x": 6, "y": 16},
                "datasource": {"type": "hadesarchitect-cassandra-datasource", "uid": ds_uid},
                "targets": [{
                    "rawQuery": True,
                    "query": "SELECT current_a FROM energy_db.meter_readings WHERE meter_id = 'Universal_Meter_001' ORDER BY timestamp DESC LIMIT 1 ALLOW FILTERING",
                    "refId": "A"
                }],
                "fieldConfig": {"defaults": {"unit": "amp"}}
            },
            {
                "id": 8,
                "title": "📋 LIVE STATUS LOG",
                "type": "table",
                "gridPos": {"h": 6, "w": 12, "x": 12, "y": 16},
                "datasource": {"type": "hadesarchitect-cassandra-datasource", "uid": ds_uid},
                "targets": [{
                    "rawQuery": True,
                    "query": "SELECT timestamp, power_w, status, anomaly_score FROM energy_db.meter_readings WHERE meter_id = 'Universal_Meter_001' LIMIT 20 ALLOW FILTERING",
                    "refId": "A"
                }],
                "fieldConfig": {
                    "defaults": {"custom": {"displayMode": "auto"}},
                    "overrides": [
                         {"matcher": {"id": "byName", "options": "status"}, "properties": [{"id": "mappings", "value": [{"type": "value", "options": {"CRITICAL": {"color": "red", "index": 0}, "Normal": {"color": "green", "index": 1}}}]}]}
                    ]
                }
            }
        ]
    },
    "overwrite": True
}

# ---------------------------------------------------------
# STEP 3: PUSH TO GRAFANA
# ---------------------------------------------------------
try:
    resp = requests.post(f"{GRAFANA_URL}/api/dashboards/db", auth=AUTH, json=dashboard_json, headers=HEADERS)
    if resp.status_code == 200:
        print("\n✅ DASHBOARD UPDATED SUCCESSFULLY!")
        print(f"👉 OPEN HERE: {GRAFANA_URL}/d/spark-brain-mission-control")
    else:
        print(f"\n❌ Upload Failed: {resp.text}")
except Exception as e:
    print(f"❌ Error contacting Grafana: {e}")