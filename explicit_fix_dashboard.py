"""
PERFECT FIX - Rebuild dashboards with EXPLICIT queries
Ensures NO confusion between columns
"""

import requests
import json
import time

GRAFANA_URL = "http://localhost:3000"
GRAFANA_USER = "admin"
GRAFANA_PASS = "admin"

headers = {
    "Authorization": f"Bearer admin",
    "Content-Type": "application/json"
}

def delete_all_dashboards():
    """Delete all dashboards first"""
    print("🧹 Deleting old dashboards...")
    try:
        url = f"{GRAFANA_URL}/api/search?query=&"
        response = requests.get(url, headers=headers, auth=(GRAFANA_USER, GRAFANA_PASS), timeout=5)
        
        if response.status_code == 200:
            dashboards = response.json()
            for dashboard in dashboards:
                if dashboard['type'] == 'dash-db':
                    delete_url = f"{GRAFANA_URL}/api/dashboards/uid/{dashboard['uid']}"
                    requests.delete(delete_url, headers=headers, auth=(GRAFANA_USER, GRAFANA_PASS), timeout=5)
            print("✅ All deleted\n")
    except:
        pass

def create_apartment_dashboard():
    """Create apartment dashboard with EXPLICIT panel queries"""
    
    url = f"{GRAFANA_URL}/api/dashboards/db"
    
    dashboard = {
        "dashboard": {
            "title": "🏠 APARTMENT MONITOR - Explicit Queries",
            "tags": ["energy", "monitoring"],
            "timezone": "browser",
            "refresh": "1s",
            "time": {"from": "now-1h", "to": "now"},
            "panels": [
                # ANOMALY SCORE - EXPLICIT COLUMN ONLY
                {
                    "id": 1,
                    "type": "stat",
                    "title": "⚠️ ANOMALY SCORE (Should be 0.0-1.0)",
                    "gridPos": {"h": 3, "w": 12, "x": 0, "y": 0},
                    "targets": [{
                        "format": "table",
                        "rawQuery": True,
                        "query": "SELECT anomaly_score FROM meter_readings WHERE meter_id='apartment_001' ORDER BY timestamp DESC LIMIT 1"
                    }],
                    "fieldConfig": {
                        "defaults": {
                            "unit": "none",
                            "decimals": 3,
                            "color": {"mode": "thresholds"},
                            "thresholds": {
                                "mode": "absolute",
                                "steps": [
                                    {"color": "green", "value": 0},
                                    {"color": "yellow", "value": 0.3},
                                    {"color": "orange", "value": 0.7},
                                    {"color": "red", "value": 0.85}
                                ]
                            },
                            "max": 1,
                            "min": 0
                        }
                    },
                    "options": {
                        "colorMode": "background",
                        "graphMode": "none",
                        "justifyMode": "center",
                        "reduceOptions": {"values": False, "fields": "", "calcs": ["lastNotNull"]}
                    }
                },
                # POWER - EXPLICIT COLUMN ONLY
                {
                    "id": 2,
                    "type": "stat",
                    "title": "🔌 POWER (Watts)",
                    "gridPos": {"h": 3, "w": 12, "x": 12, "y": 0},
                    "targets": [{
                        "format": "table",
                        "rawQuery": True,
                        "query": "SELECT power_w FROM meter_readings WHERE meter_id='apartment_001' ORDER BY timestamp DESC LIMIT 1"
                    }],
                    "fieldConfig": {
                        "defaults": {
                            "unit": "watt",
                            "decimals": 2,
                            "color": {"mode": "thresholds"},
                            "thresholds": {"mode": "absolute", "steps": [{"color": "green", "value": 0}]}
                        }
                    }
                },
                # VOLTAGE - EXPLICIT COLUMN ONLY
                {
                    "id": 3,
                    "type": "stat",
                    "title": "⚡ VOLTAGE (Volts)",
                    "gridPos": {"h": 3, "w": 8, "x": 0, "y": 3},
                    "targets": [{
                        "format": "table",
                        "rawQuery": True,
                        "query": "SELECT voltage_v FROM meter_readings WHERE meter_id='apartment_001' ORDER BY timestamp DESC LIMIT 1"
                    }],
                    "fieldConfig": {
                        "defaults": {
                            "unit": "volt",
                            "decimals": 2,
                            "color": {"mode": "thresholds"},
                            "thresholds": {"mode": "absolute", "steps": [{"color": "green", "value": 0}]}
                        }
                    }
                },
                # CURRENT - EXPLICIT COLUMN ONLY
                {
                    "id": 4,
                    "type": "stat",
                    "title": "📍 CURRENT (Amperes)",
                    "gridPos": {"h": 3, "w": 8, "x": 8, "y": 3},
                    "targets": [{
                        "format": "table",
                        "rawQuery": True,
                        "query": "SELECT current_a FROM meter_readings WHERE meter_id='apartment_001' ORDER BY timestamp DESC LIMIT 1"
                    }],
                    "fieldConfig": {
                        "defaults": {
                            "unit": "ampere",
                            "decimals": 2,
                            "color": {"mode": "thresholds"},
                            "thresholds": {"mode": "absolute", "steps": [{"color": "green", "value": 0}]}
                        }
                    }
                },
                # FREQUENCY - EXPLICIT COLUMN ONLY
                {
                    "id": 5,
                    "type": "stat",
                    "title": "📶 FREQUENCY (Hz)",
                    "gridPos": {"h": 3, "w": 8, "x": 16, "y": 3},
                    "targets": [{
                        "format": "table",
                        "rawQuery": True,
                        "query": "SELECT frequency_hz FROM meter_readings WHERE meter_id='apartment_001' ORDER BY timestamp DESC LIMIT 1"
                    }],
                    "fieldConfig": {
                        "defaults": {
                            "unit": "hertz",
                            "decimals": 2,
                            "color": {"mode": "thresholds"},
                            "thresholds": {"mode": "absolute", "steps": [{"color": "green", "value": 0}]}
                        }
                    }
                },
                # LATEST TABLE - All columns explicitly listed
                {
                    "id": 6,
                    "type": "table",
                    "title": "📊 Latest 10 Readings (Anomaly Score 0.0-1.0)",
                    "gridPos": {"h": 10, "w": 24, "x": 0, "y": 6},
                    "targets": [{
                        "format": "table",
                        "rawQuery": True,
                        "query": "SELECT timestamp, power_w, voltage_v, current_a, frequency_hz, anomaly_score FROM meter_readings WHERE meter_id='apartment_001' ORDER BY timestamp DESC LIMIT 10"
                    }],
                    "fieldConfig": {
                        "defaults": {
                            "custom": {"hideFrom": {"legend": False, "tooltip": False, "viz": False}}
                        },
                        "overrides": [
                            {"matcher": {"id": "byName", "options": "anomaly_score"}, "properties": [{"id": "unit", "value": "none"}, {"id": "decimals", "value": 4}]},
                            {"matcher": {"id": "byName", "options": "power_w"}, "properties": [{"id": "unit", "value": "watt"}, {"id": "decimals", "value": 2}]},
                            {"matcher": {"id": "byName", "options": "voltage_v"}, "properties": [{"id": "unit", "value": "volt"}, {"id": "decimals", "value": 2}]},
                            {"matcher": {"id": "byName", "options": "current_a"}, "properties": [{"id": "unit", "value": "ampere"}, {"id": "decimals", "value": 2}]},
                            {"matcher": {"id": "byName", "options": "frequency_hz"}, "properties": [{"id": "unit", "value": "hertz"}, {"id": "decimals", "value": 3}]}
                        ]
                    }
                }
            ]
        }
    }
    
    try:
        response = requests.post(url, json=dashboard, headers=headers, 
                                auth=(GRAFANA_USER, GRAFANA_PASS), timeout=10)
        if response.status_code in [200, 409]:
            print(f"✅ Created APARTMENT dashboard (Explicit Queries)")
            return True
    except Exception as e:
        print(f"❌ Error: {e}")
    return False

def main():
    print("\n" + "="*70)
    print("🔧 EXPLICIT QUERY FIX - Rebuild with Clear Column Mappings")
    print("="*70 + "\n")
    
    delete_all_dashboards()
    time.sleep(2)
    
    print("📊 Creating dashboard with EXPLICIT SINGLE-COLUMN queries...\n")
    
    if create_apartment_dashboard():
        print("\n" + "="*70)
        print("✅ APARTMENT DASHBOARD READY")
        print("="*70)
        print("\n📊 Panel Queries:")
        print("   • ANOMALY SCORE: SELECT anomaly_score (should be 0.0-1.0)")
        print("   • POWER: SELECT power_w (should be 100-250W)")
        print("   • VOLTAGE: SELECT voltage_v (should be 226-232V)")
        print("   • CURRENT: SELECT current_a (should be 0.5-1.0A)")
        print("   • FREQUENCY: SELECT frequency_hz (should be ~50Hz)")
        print("   • TABLE: All columns explicit with correct units\n")
        print("🌐 Open Grafana: http://localhost:3000")
        print("✅ Check ANOMALY SCORE panel - should show decimals like 0.650, 0.720, etc.\n")

if __name__ == "__main__":
    main()
