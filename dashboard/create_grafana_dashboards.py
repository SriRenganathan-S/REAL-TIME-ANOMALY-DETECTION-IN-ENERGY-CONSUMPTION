"""
GRAFANA DASHBOARD SETUP - Phase 3C
Creates 6 comprehensive dashboards:
1. Apartment Overview
2. Suburban Home Overview
3. Automobile Factory Overview
4. Shopping Mall Overview
5. Textile Mill Overview
6. Master Overview (all 5 meters)
"""

import requests
import json
import time

GRAFANA_URL = "http://localhost:3000"
GRAFANA_USER = "admin"
GRAFANA_PASS = "admin"

# Grafana API endpoints
headers = {
    "Authorization": f"Bearer admin",
    "Content-Type": "application/json"
}

def create_datasource():
    """Create Cassandra datasource in Grafana"""
    url = f"{GRAFANA_URL}/api/datasources"
    
    datasource = {
        "name": "Cassandra Energy DB",
        "type": "cassandra-datasource",
        "access": "proxy",
        "isDefault": True,
        "jsonData": {
            "keyspace": "energy_db",
            "host": "cassandra_db",
            "port": 9042,
            "userName": "cassandra",
            "password": "cassandra"
        }
    }
    
    try:
        response = requests.post(url, json=datasource, headers=headers, auth=(GRAFANA_USER, GRAFANA_PASS))
        if response.status_code in [200, 409]:  # 409 = already exists
            print("✅ Cassandra datasource configured")
            return True
    except Exception as e:
        print(f"⚠️  Datasource setup: {e}")
        # Use TestData datasource instead for now
        return setup_testdata_ds()

def setup_testdata_ds():
    """Setup TestData datasource as fallback"""
    url = f"{GRAFANA_URL}/api/datasources"
    
    datasource = {
        "name": "TestData",
        "type": "testdata",
        "access": "proxy",
        "isDefault": True,
        "jsonData": {}
    }
    
    try:
        response = requests.post(url, json=datasource, headers=headers, auth=(GRAFANA_USER, GRAFANA_PASS))
        print(f"✅ TestData datasource setup ({response.status_code})")
        return True
    except Exception as e:
        print(f"❌ TestData datasource failed: {e}")
        return False

def create_dashboard(title, meter_id, meter_label, color):
    """Create a meter dashboard"""
    
    url = f"{GRAFANA_URL}/api/dashboards/db"
    
    dashboard = {
        "dashboard": {
            "title": title,
            "tags": ["energy-monitoring", "multi-meter", meter_id],
            "timezone": "browser",
            "panels": [
                # Panel 1: Power Timeline with background colors for anomalies
                {
                    "id": 1,
                    "title": f"{meter_label} - Real-Time Power Consumption",
                    "type": "timeseries",
                    "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0},
                    "targets": [
                        {
                            "format": "time_series",
                            "rawQuery": True,
                            "query": f"SELECT timestamp, power_w FROM meter_readings WHERE meter_id='{meter_id}' ORDER BY timestamp DESC LIMIT 1000"
                        }
                    ],
                    "fieldConfig": {
                        "defaults": {
                            "custom": {"lineWidth": 2},
                            "color": {"mode": "fixed", "fixedColor": color},
                            "unit": "short"
                        }
                    }
                },
                # Panel 2: Anomaly Score with Live Value
                {
                    "id": 2,
                    "title": f"{meter_label} - ANOMALY SCORE",
                    "type": "gauge",
                    "gridPos": {"h": 8, "w": 6, "x": 12, "y": 0},
                    "targets": [
                        {
                            "format": "table",
                            "rawQuery": True,
                            "query": f"SELECT anomaly_score FROM meter_readings WHERE meter_id='{meter_id}' ORDER BY timestamp DESC LIMIT 1"
                        }
                    ],
                    "fieldConfig": {
                        "defaults": {
                            "color": {"mode": "thresholds"},
                            "thresholds": {
                                "mode": "absolute",
                                "steps": [
                                    {"color": "green", "value": None},
                                    {"color": "yellow", "value": 0.3},
                                    {"color": "orange", "value": 0.7},
                                    {"color": "red", "value": 0.85}
                                ]
                            },
                            "max": 1,
                            "min": 0,
                            "unit": "percentunit"
                        }
                    }
                },
                # Panel 2B: Anomaly Timeline
                {
                    "id": 9,
                    "title": f"{meter_label} - Anomaly Score Timeline",
                    "type": "timeseries",
                    "gridPos": {"h": 8, "w": 6, "x": 18, "y": 0},
                    "targets": [
                        {
                            "format": "time_series",
                            "rawQuery": True,
                            "query": f"SELECT timestamp, anomaly_score FROM meter_readings WHERE meter_id='{meter_id}' ORDER BY timestamp DESC LIMIT 1000"
                        }
                    ],
                    "fieldConfig": {
                        "defaults": {
                            "custom": {"lineWidth": 2},
                            "color": {"mode": "thresholds"},
                            "thresholds": {
                                "mode": "absolute",
                                "steps": [
                                    {"color": "green", "value": None},
                                    {"color": "yellow", "value": 0.3},
                                    {"color": "orange", "value": 0.7},
                                    {"color": "red", "value": 0.85}
                                ]
                            },
                            "max": 1,
                            "min": 0
                        }
                    }
                },
                # Panel 3: Risk Level Gauge
                {
                    "id": 3,
                    "title": f"{meter_label} - Current Risk Level",
                    "type": "stat",
                    "gridPos": {"h": 4, "w": 6, "x": 0, "y": 8},
                    "targets": [
                        {
                            "format": "table",
                            "rawQuery": True,
                            "query": f"SELECT risk_level FROM meter_readings WHERE meter_id='{meter_id}' ORDER BY timestamp DESC LIMIT 1"
                        }
                    ]
                },
                # Panel 4: Status
                {
                    "id": 4,
                    "title": f"{meter_label} - Latest Status",
                    "type": "stat",
                    "gridPos": {"h": 4, "w": 6, "x": 6, "y": 8},
                    "targets": [
                        {
                            "format": "table",
                            "rawQuery": True,
                            "query": f"SELECT status FROM meter_readings WHERE meter_id='{meter_id}' ORDER BY timestamp DESC LIMIT 1"
                        }
                    ]
                },
                # Panel 5: Fault Type Distribution
                {
                    "id": 5,
                    "title": f"{meter_label} - Detected Fault Types",
                    "type": "piechart",
                    "gridPos": {"h": 4, "w": 6, "x": 12, "y": 8},
                    "targets": [
                        {
                            "format": "table",
                            "rawQuery": True,
                            "query": f"SELECT fault_type, COUNT(*) as count FROM meter_readings WHERE meter_id='{meter_id}' GROUP BY fault_type"
                        }
                    ]
                },
                # Panel 6: Voltage stability
                {
                    "id": 6,
                    "title": f"{meter_label} - Voltage Stability (V)",
                    "type": "timeseries",
                    "gridPos": {"h": 4, "w": 6, "x": 18, "y": 8},
                    "targets": [
                        {
                            "format": "time_series",
                            "rawQuery": True,
                            "query": f"SELECT timestamp, voltage_v FROM meter_readings WHERE meter_id='{meter_id}' ORDER BY timestamp DESC LIMIT 1000"
                        }
                    ],
                    "fieldConfig": {
                        "defaults": {
                            "custom": {"lineWidth": 1},
                            "color": {"mode": "fixed", "fixedColor": "blue"},
                            "min": 220,
                            "max": 240
                        }
                    }
                },
                # Panel 7: Learning Progress (Hidden in Details)
                {
                    "id": 7,
                    "title": f"{meter_label} - Model Learning Count",
                    "type": "stat",
                    "gridPos": {"h": 0, "w": 0, "x": 0, "y": 12},
                    "hidden": True,
                    "targets": [
                        {
                            "format": "table",
                            "rawQuery": True,
                            "query": f"SELECT learning_count FROM model_states WHERE meter_id='{meter_id}' ORDER BY last_updated DESC LIMIT 1"
                        }
                    ]
                },
                # Panel 8: Recent Alerts
                {
                    "id": 8,
                    "title": f"{meter_label} - Recent CRITICAL Alerts",
                    "type": "table",
                    "gridPos": {"h": 4, "w": 20, "x": 0, "y": 14},
                    "targets": [
                        {
                            "format": "table",
                            "rawQuery": True,
                            "query": f"SELECT timestamp, power_w, anomaly_score, risk_level, fault_type FROM meter_readings WHERE meter_id='{meter_id}' AND status='CRITICAL' ORDER BY timestamp DESC LIMIT 20"
                        }
                    ]
                }
            ],
            "schemaVersion": 27,
            "style": "dark",
            "refresh": "1s"
        },
        "overwrite": True
    }
    
    try:
        response = requests.post(url, json=dashboard, headers=headers, auth=(GRAFANA_USER, GRAFANA_PASS))
        if response.status_code in [200, 409]:
            print(f"✅ Dashboard created: {title}")
            return True
        else:
            print(f"⚠️  Dashboard {title}: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Dashboard {title} failed: {e}")
        return False

def create_master_dashboard():
    """Create master dashboard comparing all 5 meters"""
    
    url = f"{GRAFANA_URL}/api/dashboards/db"
    
    dashboard = {
        "dashboard": {
            "title": "Master Overview - All 5 Meters LIVE",
            "tags": ["energy-monitoring", "master", "overview"],
            "timezone": "browser",
            "panels": [
                {
                    "id": 1,
                    "title": "All Meters - Power Consumption Comparison",
                    "type": "timeseries",
                    "gridPos": {"h": 10, "w": 24, "x": 0, "y": 0},
                    "targets": [
                        {
                            "format": "time_series",
                            "rawQuery": True,
                            "query": "SELECT timestamp, meter_id, power_w FROM meter_readings WHERE meter_id IN ('apartment_001', 'suburban_home_001', 'auto_factory_001', 'shopping_mall_001', 'textile_mill_001') ORDER BY timestamp DESC LIMIT 2000"
                        }
                    ]
                },
                {
                    "id": 2,
                    "title": "5-Meter Anomaly Scores (Color Coded)",
                    "type": "timeseries",
                    "gridPos": {"h": 10, "w": 24, "x": 0, "y": 10},
                    "targets": [
                        {
                            "format": "time_series",
                            "rawQuery": True,
                            "query": "SELECT timestamp, meter_id, anomaly_score FROM meter_readings WHERE meter_id IN ('apartment_001', 'suburban_home_001', 'auto_factory_001', 'shopping_mall_001', 'textile_mill_001') ORDER BY timestamp DESC LIMIT 5000"
                        }
                    ],
                    "fieldConfig": {
                        "defaults": {
                            "custom": {"lineWidth": 2},
                            "color": {"mode": "thresholds"},
                            "thresholds": {
                                "mode": "absolute",
                                "steps": [
                                    {"color": "green", "value": None},
                                    {"color": "yellow", "value": 0.3},
                                    {"color": "orange", "value": 0.7},
                                    {"color": "red", "value": 0.85}
                                ]
                            }
                        }
                    }
                },
                {
                    "id": 3,
                    "title": "Active Alerts - Risk Distribution",
                    "type": "piechart",
                    "gridPos": {"h": 8, "w": 12, "x": 0, "y": 20},
                    "targets": [
                        {
                            "format": "table",
                            "rawQuery": True,
                            "query": "SELECT risk_level, COUNT(*) as alert_count FROM meter_readings WHERE risk_level != 'NORMAL' GROUP BY risk_level"
                        }
                    ]
                },
                {
                    "id": 4,
                    "title": "System Health - Meters Online",
                    "type": "stat",
                    "gridPos": {"h": 8, "w": 12, "x": 12, "y": 20},
                    "targets": [
                        {
                            "format": "table",
                            "rawQuery": True,
                            "query": "SELECT COUNT(DISTINCT meter_id) as online_meters FROM meter_readings"
                        }
                    ]
                }
            ],
            "schemaVersion": 27,
            "style": "dark",
            "refresh": "1s"
        },
        "overwrite": True
    }
    
    try:
        response = requests.post(url, json=dashboard, headers=headers, auth=(GRAFANA_USER, GRAFANA_PASS))
        if response.status_code in [200, 409]:
            print(f"✅ Master dashboard created")
            return True
        else:
            print(f"⚠️  Master dashboard: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Master dashboard failed: {e}")
        return False

# Main execution
if __name__ == "__main__":
    print("[GRAFANA] Starting dashboard setup...")
    
    # Wait for Grafana to be ready
    time.sleep(2)
    
    # Create datasource
    create_datasource()
    
    # Create individual meter dashboards
    meters = [
        ("Apartment Monitor", "apartment_001", "Apartment (150W-1500W)", "green"),
        ("Suburban Home Monitor", "suburban_home_001", "Suburban Home (300W-4500W)", "blue"),
        ("Automobile Factory Monitor", "auto_factory_001", "Auto Factory (50kW-200kW)", "orange"),
        ("Shopping Mall Monitor", "shopping_mall_001", "Shopping Mall (80kW-500kW)", "purple"),
        ("Textile Mill Monitor", "textile_mill_001", "Textile Mill (100kW-250kW)", "red"),
    ]
    
    for title, meter_id, label, color in meters:
        create_dashboard(title, meter_id, label, color)
        time.sleep(0.5)
    
    # Create master dashboard
    create_master_dashboard()
    
    print("\n[DONE] All dashboards created! Access Grafana at http://localhost:3000")
    print("Login: admin / admin")
