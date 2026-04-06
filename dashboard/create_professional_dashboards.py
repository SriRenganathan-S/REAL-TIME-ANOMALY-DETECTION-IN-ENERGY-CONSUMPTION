"""
PROFESSIONAL GRAFANA DASHBOARDS - PRODUCTION GRADE
Creates 6 user-focused, production-ready dashboards
Refresh Rate: 1 second (LIVE UPDATES)
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

def setup_datasource():
    """Ensure Cassandra datasource is configured"""
    url = f"{GRAFANA_URL}/api/datasources"
    
    datasource = {
        "name": "Cassandra DB",
        "type": "cassandra-datasource",
        "access": "proxy",
        "isDefault": True,
        "jsonData": {
            "keyspace": "energy_db",
            "host": "cassandra_db",
            "port": 9042
        }
    }
    
    try:
        response = requests.post(url, json=datasource, headers=headers, 
                                auth=(GRAFANA_USER, GRAFANA_PASS), timeout=5)
        if response.status_code in [200, 409]:
            print("✅ Datasource ready")
            return True
    except:
        pass
    return True

def create_apartment_dashboard():
    """APARTMENT MONITOR - 150W-1500W (Residential)"""
    
    url = f"{GRAFANA_URL}/api/dashboards/db"
    
    dashboard = {
        "dashboard": {
            "title": "🏠 APARTMENT MONITOR - Real-Time Energy",
            "description": "Apartment residential unit monitoring (150W-1500W range)",
            "tags": ["residential", "apartment", "energy-monitoring"],
            "timezone": "browser",
            "refresh": "1s",
            "time": {"from": "now-1h", "to": "now"},
            "panels": [
                # Row 1: Status Header
                {
                    "id": 1,
                    "type": "stat",
                    "title": "CURRENT STATUS",
                    "gridPos": {"h": 2, "w": 6, "x": 0, "y": 0},
                    "targets": [{
                        "format": "table",
                        "rawQuery": True,
                        "query": "SELECT status FROM meter_readings WHERE meter_id='apartment_001' ORDER BY timestamp DESC LIMIT 1"
                    }],
                    "fieldConfig": {
                        "defaults": {
                            "mappings": [
                                {"type": "value", "options": {"1": {"text": "ONLINE ✅", "color": "green"}}},
                            ],
                            "thresholds": {"mode": "absolute", "steps": [{"color": "green", "value": None}]}
                        }
                    }
                },
                {
                    "id": 2,
                    "type": "stat",
                    "title": "ANOMALY SCORE",
                    "gridPos": {"h": 2, "w": 6, "x": 6, "y": 0},
                    "targets": [{
                        "format": "table",
                        "rawQuery": True,
                        "query": "SELECT anomaly_score FROM meter_readings WHERE meter_id='apartment_001' ORDER BY timestamp DESC LIMIT 1"
                    }],
                    "fieldConfig": {
                        "defaults": {
                            "unit": "none",
                            "decimals": 3,
                            "custom": {"hideFrom": {"legend": False, "tooltip": False, "viz": False}},
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
                            "min": 0,
                            "mappings": []
                        }
                    }
                },
                {
                    "id": 3,
                    "type": "stat",
                    "title": "LAST UPDATED",
                    "gridPos": {"h": 2, "w": 6, "x": 12, "y": 0},
                    "targets": [{
                        "format": "table",
                        "rawQuery": True,
                        "query": "SELECT timestamp FROM meter_readings WHERE meter_id='apartment_001' ORDER BY timestamp DESC LIMIT 1"
                    }]
                },
                {
                    "id": 4,
                    "type": "stat",
                    "title": "RISK LEVEL",
                    "gridPos": {"h": 2, "w": 6, "x": 18, "y": 0},
                    "targets": [{
                        "format": "table",
                        "rawQuery": True,
                        "query": "SELECT risk_level FROM meter_readings WHERE meter_id='apartment_001' ORDER BY timestamp DESC LIMIT 1"
                    }],
                    "fieldConfig": {
                        "defaults": {
                            "mappings": [
                                {"type": "value", "options": {"NORMAL": {"text": "NORMAL", "color": "green"}, "ALERT": {"text": "ALERT", "color": "yellow"}, "CRITICAL": {"text": "CRITICAL", "color": "red"}}}
                            ]
                        }
                    }
                },
                # Row 2: Main Metrics (Live Values)
                {
                    "id": 5,
                    "type": "gauge",
                    "title": "Real-Time Power Load",
                    "gridPos": {"h": 8, "w": 6, "x": 0, "y": 2},
                    "targets": [{
                        "format": "table",
                        "rawQuery": True,
                        "query": "SELECT power_w FROM meter_readings WHERE meter_id='apartment_001' ORDER BY timestamp DESC LIMIT 1"
                    }],
                    "fieldConfig": {
                        "defaults": {
                            "unit": "watt",
                            "color": {"mode": "thresholds"},
                            "thresholds": {
                                "mode": "absolute",
                                "steps": [
                                    {"color": "green", "value": None},
                                    {"color": "yellow", "value": 750},
                                    {"color": "orange", "value": 1200},
                                    {"color": "red", "value": 1400}
                                ]
                            },
                            "max": 1500,
                            "min": 0
                        }
                    }
                },
                {
                    "id": 6,
                    "type": "stat",
                    "title": "Voltage (V)",
                    "gridPos": {"h": 4, "w": 3, "x": 6, "y": 2},
                    "targets": [{
                        "format": "table",
                        "rawQuery": True,
                        "query": "SELECT voltage_v FROM meter_readings WHERE meter_id='apartment_001' ORDER BY timestamp DESC LIMIT 1"
                    }],
                    "fieldConfig": {
                        "defaults": {
                            "unit": "volt",
                            "thresholds": {
                                "mode": "absolute",
                                "steps": [
                                    {"color": "red", "value": None},
                                    {"color": "yellow", "value": 220},
                                    {"color": "green", "value": 225},
                                    {"color": "yellow", "value": 240}
                                ]
                            }
                        }
                    }
                },
                {
                    "id": 7,
                    "type": "stat",
                    "title": "Current (A)",
                    "gridPos": {"h": 4, "w": 3, "x": 9, "y": 2},
                    "targets": [{
                        "format": "table",
                        "rawQuery": True,
                        "query": "SELECT current_a FROM meter_readings WHERE meter_id='apartment_001' ORDER BY timestamp DESC LIMIT 1"
                    }],
                    "fieldConfig": {
                        "defaults": {"unit": "amp"}
                    }
                },
                {
                    "id": 8,
                    "type": "stat",
                    "title": "Frequency (Hz)",
                    "gridPos": {"h": 4, "w": 3, "x": 12, "y": 2},
                    "targets": [{
                        "format": "table",
                        "rawQuery": True,
                        "query": "SELECT frequency_hz FROM meter_readings WHERE meter_id='apartment_001' ORDER BY timestamp DESC LIMIT 1"
                    }],
                    "fieldConfig": {
                        "defaults": {"unit": "short"}
                    }
                },
                {
                    "id": 9,
                    "type": "stat",
                    "title": "Fault Detected",
                    "gridPos": {"h": 4, "w": 3, "x": 15, "y": 2},
                    "targets": [{
                        "format": "table",
                        "rawQuery": True,
                        "query": "SELECT fault_type FROM meter_readings WHERE meter_id='apartment_001' ORDER BY timestamp DESC LIMIT 1"
                    }]
                },
                {
                    "id": 10,
                    "type": "stat",
                    "title": "Data Latency",
                    "gridPos": {"h": 4, "w": 3, "x": 18, "y": 2},
                    "targets": [{
                        "format": "table",
                        "rawQuery": True,
                        "query": "SELECT latency_ms FROM meter_readings WHERE meter_id='apartment_001' ORDER BY timestamp DESC LIMIT 1"
                    }],
                    "fieldConfig": {
                        "defaults": {"unit": "ms"}
                    }
                },
                {
                    "id": 11,
                    "type": "stat",
                    "title": "Daily Average",
                    "gridPos": {"h": 4, "w": 3, "x": 21, "y": 2},
                    "targets": [{
                        "format": "table",
                        "rawQuery": True,
                        "query": "SELECT AVG(power_w) as avg_power FROM meter_readings WHERE meter_id='apartment_001' AND timestamp > now() - 86400000"
                    }],
                    "fieldConfig": {
                        "defaults": {"unit": "watt"}
                    }
                },
                # Row 3: Power Consumption Timeline
                {
                    "id": 12,
                    "type": "timeseries",
                    "title": "Power Consumption Trend (Last Hour)",
                    "gridPos": {"h": 8, "w": 12, "x": 0, "y": 10},
                    "targets": [{
                        "format": "time_series",
                        "rawQuery": True,
                        "query": "SELECT timestamp, power_w FROM meter_readings WHERE meter_id='apartment_001' ORDER BY timestamp DESC LIMIT 3600"
                    }],
                    "fieldConfig": {
                        "defaults": {
                            "custom": {"lineWidth": 2, "fillOpacity": 10},
                            "color": {"mode": "fixed", "fixedColor": "green"},
                            "unit": "watt"
                        }
                    }
                },
                # Row 3: Anomaly Timeline
                {
                    "id": 13,
                    "type": "timeseries",
                    "title": "Anomaly Score Timeline (Last Hour)",
                    "gridPos": {"h": 8, "w": 12, "x": 12, "y": 10},
                    "targets": [{
                        "format": "time_series",
                        "rawQuery": True,
                        "query": "SELECT timestamp, anomaly_score FROM meter_readings WHERE meter_id='apartment_001' ORDER BY timestamp DESC LIMIT 3600"
                    }],
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
                # Row 4: Recent Alerts Table
                {
                    "id": 14,
                    "type": "table",
                    "title": "🔴 Recent Critical Events (Last 24 Hours)",
                    "gridPos": {"h": 8, "w": 24, "x": 0, "y": 18},
                    "targets": [{
                        "format": "table",
                        "rawQuery": True,
                        "query": "SELECT timestamp, power_w, anomaly_score, voltage_v, current_a, fault_type FROM meter_readings WHERE meter_id='apartment_001' AND anomaly_score > 0.7 ORDER BY timestamp DESC LIMIT 20"
                    }]
                }
            ],
            "schemaVersion": 38,
            "style": "dark",
            "templating": {"list": []},
            "annotations": {"list": []}
        },
        "overwrite": True
    }
    
    try:
        response = requests.post(url, json=dashboard, headers=headers, 
                                auth=(GRAFANA_USER, GRAFANA_PASS), timeout=10)
        if response.status_code in [200, 409]:
            print("✅ Apartment Monitor Dashboard created")
            return True
    except Exception as e:
        print(f"❌ Apartment Dashboard: {e}")
    return False

def create_suburban_dashboard():
    """SUBURBAN HOME MONITOR - 300W-4500W"""
    
    url = f"{GRAFANA_URL}/api/dashboards/db"
    
    dashboard = {
        "dashboard": {
            "title": "🏡 SUBURBAN HOME MONITOR - Smart Living",
            "description": "Suburban home with HVAC, heating, pooling (300W-4500W)",
            "tags": ["residential", "suburban", "energy-monitoring"],
            "timezone": "browser",
            "refresh": "1s",
            "time": {"from": "now-1h", "to": "now"},
            "panels": [
                # Status Row
                {
                    "id": 1,
                    "type": "stat",
                    "title": "SYSTEM STATUS",
                    "gridPos": {"h": 2, "w": 6, "x": 0, "y": 0},
                    "targets": [{
                        "format": "table",
                        "rawQuery": True,
                        "query": "SELECT status FROM meter_readings WHERE meter_id='suburban_home_001' ORDER BY timestamp DESC LIMIT 1"
                    }],
                    "fieldConfig": {
                        "defaults": {
                            "mappings": [
                                {"type": "value", "options": {"1": {"text": "ONLINE ✅", "color": "green"}}},
                            ],
                            "color": {"mode": "fixed", "fixedColor": "blue"}
                        }
                    }
                },
                {
                    "id": 2,
                    "type": "stat",
                    "title": "ANOMALY SCORE",
                    "gridPos": {"h": 2, "w": 6, "x": 6, "y": 0},
                    "targets": [{
                        "format": "table",
                        "rawQuery": True,
                        "query": "SELECT anomaly_score FROM meter_readings WHERE meter_id='suburban_home_001' ORDER BY timestamp DESC LIMIT 1"
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
                            "min": 0,
                            "mappings": []
                        }
                    }
                },
                {
                    "id": 3,
                    "type": "stat",
                    "title": "ALERT STATUS",
                    "gridPos": {"h": 2, "w": 6, "x": 12, "y": 0},
                    "targets": [{
                        "format": "table",
                        "rawQuery": True,
                        "query": "SELECT risk_level FROM meter_readings WHERE meter_id='suburban_home_001' ORDER BY timestamp DESC LIMIT 1"
                    }],
                    "fieldConfig": {
                        "defaults": {
                            "mappings": [
                                {"type": "value", "options": {"NORMAL": {"text": "✅ NORMAL", "color": "green"}, "ALERT": {"text": "⚠️ ALERT", "color": "orange"}, "CRITICAL": {"text": "🔴 CRITICAL", "color": "red"}}}
                            ]
                        }
                    }
                },
                {
                    "id": 4,
                    "type": "stat",
                    "title": "PEAK TODAY",
                    "gridPos": {"h": 2, "w": 6, "x": 18, "y": 0},
                    "targets": [{
                        "format": "table",
                        "rawQuery": True,
                        "query": "SELECT MAX(power_w) as peak_power FROM meter_readings WHERE meter_id='suburban_home_001' AND timestamp > now() - 86400000"
                    }],
                    "fieldConfig": {
                        "defaults": {"unit": "watt"}
                    }
                },
                # Gauges
                {
                    "id": 5,
                    "type": "gauge",
                    "title": "Real-Time Power Load",
                    "gridPos": {"h": 8, "w": 6, "x": 0, "y": 2},
                    "targets": [{
                        "format": "table",
                        "rawQuery": True,
                        "query": "SELECT power_w FROM meter_readings WHERE meter_id='suburban_home_001' ORDER BY timestamp DESC LIMIT 1"
                    }],
                    "fieldConfig": {
                        "defaults": {
                            "unit": "watt",
                            "color": {"mode": "thresholds"},
                            "thresholds": {
                                "mode": "absolute",
                                "steps": [
                                    {"color": "green", "value": None},
                                    {"color": "yellow", "value": 1500},
                                    {"color": "orange", "value": 3000},
                                    {"color": "red", "value": 4200}
                                ]
                            },
                            "max": 4500,
                            "min": 0
                        }
                    }
                },
                {
                    "id": 6,
                    "type": "stat",
                    "title": "Voltage (V)",
                    "gridPos": {"h": 4, "w": 3, "x": 6, "y": 2},
                    "targets": [{
                        "format": "table",
                        "rawQuery": True,
                        "query": "SELECT voltage_v FROM meter_readings WHERE meter_id='suburban_home_001' ORDER BY timestamp DESC LIMIT 1"
                    }],
                    "fieldConfig": {"defaults": {"unit": "volt"}}
                },
                {
                    "id": 7,
                    "type": "stat",
                    "title": "Current (A)",
                    "gridPos": {"h": 4, "w": 3, "x": 9, "y": 2},
                    "targets": [{
                        "format": "table",
                        "rawQuery": True,
                        "query": "SELECT current_a FROM meter_readings WHERE meter_id='suburban_home_001' ORDER BY timestamp DESC LIMIT 1"
                    }],
                    "fieldConfig": {"defaults": {"unit": "amp"}}
                },
                {
                    "id": 8,
                    "type": "stat",
                    "title": "Frequency (Hz)",
                    "gridPos": {"h": 4, "w": 3, "x": 12, "y": 2},
                    "targets": [{
                        "format": "table",
                        "rawQuery": True,
                        "query": "SELECT frequency_hz FROM meter_readings WHERE meter_id='suburban_home_001' ORDER BY timestamp DESC LIMIT 1"
                    }],
                    "fieldConfig": {"defaults": {"unit": "short"}}
                },
                {
                    "id": 9,
                    "type": "stat",
                    "title": "Issue Detected",
                    "gridPos": {"h": 4, "w": 3, "x": 15, "y": 2},
                    "targets": [{
                        "format": "table",
                        "rawQuery": True,
                        "query": "SELECT fault_type FROM meter_readings WHERE meter_id='suburban_home_001' ORDER BY timestamp DESC LIMIT 1"
                    }]
                },
                {
                    "id": 10,
                    "type": "stat",
                    "title": "Latency (ms)",
                    "gridPos": {"h": 4, "w": 3, "x": 18, "y": 2},
                    "targets": [{
                        "format": "table",
                        "rawQuery": True,
                        "query": "SELECT latency_ms FROM meter_readings WHERE meter_id='suburban_home_001' ORDER BY timestamp DESC LIMIT 1"
                    }],
                    "fieldConfig": {"defaults": {"unit": "ms"}}
                },
                {
                    "id": 11,
                    "type": "stat",
                    "title": "Daily Avg (W)",
                    "gridPos": {"h": 4, "w": 3, "x": 21, "y": 2},
                    "targets": [{
                        "format": "table",
                        "rawQuery": True,
                        "query": "SELECT AVG(power_w) as avg_power FROM meter_readings WHERE meter_id='suburban_home_001' AND timestamp > now() - 86400000"
                    }],
                    "fieldConfig": {"defaults": {"unit": "watt"}}
                },
                # Charts
                {
                    "id": 12,
                    "type": "timeseries",
                    "title": "Power Consumption Trend (Last Hour)",
                    "gridPos": {"h": 8, "w": 12, "x": 0, "y": 10},
                    "targets": [{
                        "format": "time_series",
                        "rawQuery": True,
                        "query": "SELECT timestamp, power_w FROM meter_readings WHERE meter_id='suburban_home_001' ORDER BY timestamp DESC LIMIT 3600"
                    }],
                    "fieldConfig": {
                        "defaults": {
                            "custom": {"lineWidth": 2, "fillOpacity": 10},
                            "color": {"mode": "fixed", "fixedColor": "blue"},
                            "unit": "watt"
                        }
                    }
                },
                {
                    "id": 13,
                    "type": "timeseries",
                    "title": "Anomaly Detection Timeline",
                    "gridPos": {"h": 8, "w": 12, "x": 12, "y": 10},
                    "targets": [{
                        "format": "time_series",
                        "rawQuery": True,
                        "query": "SELECT timestamp, anomaly_score FROM meter_readings WHERE meter_id='suburban_home_001' ORDER BY timestamp DESC LIMIT 3600"
                    }],
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
                # Alerts
                {
                    "id": 14,
                    "type": "table",
                    "title": "⚠️ All Anomalies (Last 24 Hours)",
                    "gridPos": {"h": 8, "w": 24, "x": 0, "y": 18},
                    "targets": [{
                        "format": "table",
                        "rawQuery": True,
                        "query": "SELECT timestamp, power_w, anomaly_score, voltage_v, current_a, fault_type, risk_level FROM meter_readings WHERE meter_id='suburban_home_001' AND anomaly_score > 0.3 ORDER BY timestamp DESC LIMIT 30"
                    }]
                }
            ],
            "schemaVersion": 38,
            "style": "dark",
            "templating": {"list": []},
            "annotations": {"list": []}
        },
        "overwrite": True
    }
    
    try:
        response = requests.post(url, json=dashboard, headers=headers, 
                                auth=(GRAFANA_USER, GRAFANA_PASS), timeout=10)
        if response.status_code in [200, 409]:
            print("✅ Suburban Home Dashboard created")
            return True
    except Exception as e:
        print(f"❌ Suburban Dashboard: {e}")
    return False

def create_factory_dashboard():
    """AUTOMOBILE FACTORY MONITOR - 50kW-200kW"""
    
    url = f"{GRAFANA_URL}/api/dashboards/db"
    
    dashboard = {
        "dashboard": {
            "title": "🏭 AUTOMOBILE FACTORY MONITOR - Production Control",
            "description": "Industrial factory assembly lines (50kW-200kW)",
            "tags": ["industrial", "factory", "production"],
            "timezone": "browser",
            "refresh": "1s",
            "time": {"from": "now-1h", "to": "now"},
            "panels": [
                # Status Header
                {
                    "id": 1,
                    "type": "stat",
                    "title": "PRODUCTION STATUS",
                    "gridPos": {"h": 2, "w": 6, "x": 0, "y": 0},
                    "targets": [{
                        "format": "table",
                        "rawQuery": True,
                        "query": "SELECT status FROM meter_readings WHERE meter_id='auto_factory_001' ORDER BY timestamp DESC LIMIT 1"
                    }],
                    "fieldConfig": {
                        "defaults": {
                            "mappings": [
                                {"type": "value", "options": {"1": {"text": "RUNNING ✅", "color": "green"}}},
                            ]
                        }
                    }
                },
                {
                    "id": 2,
                    "type": "stat",
                    "title": "ANOMALY SCORE",
                    "gridPos": {"h": 2, "w": 6, "x": 6, "y": 0},
                    "targets": [{
                        "format": "table",
                        "rawQuery": True,
                        "query": "SELECT anomaly_score FROM meter_readings WHERE meter_id='auto_factory_001' ORDER BY timestamp DESC LIMIT 1"
                    }],
                    "fieldConfig": {
                        "defaults": {
                            "unit": "short",
                            "decimals": 3,
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
                {
                    "id": 3,
                    "type": "stat",
                    "title": "RISK ALERT",
                    "gridPos": {"h": 2, "w": 6, "x": 12, "y": 0},
                    "targets": [{
                        "format": "table",
                        "rawQuery": True,
                        "query": "SELECT risk_level FROM meter_readings WHERE meter_id='auto_factory_001' ORDER BY timestamp DESC LIMIT 1"
                    }],
                    "fieldConfig": {
                        "defaults": {
                            "mappings": [
                                {"type": "value", "options": {"NORMAL": {"text": "✅", "color": "green"}, "ALERT": {"text": "⚠️", "color": "orange"}, "CRITICAL": {"text": "🔴", "color": "red"}}}
                            ]
                        }
                    }
                },
                {
                    "id": 4,
                    "type": "stat",
                    "title": "MAX LOAD TODAY",
                    "gridPos": {"h": 2, "w": 6, "x": 18, "y": 0},
                    "targets": [{
                        "format": "table",
                        "rawQuery": True,
                        "query": "SELECT MAX(power_w)/1000 as peak_kw FROM meter_readings WHERE meter_id='auto_factory_001' AND timestamp > now() - 86400000"
                    }],
                    "fieldConfig": {"defaults": {"unit": "short"}}
                },
                # Main gauge
                {
                    "id": 5,
                    "type": "gauge",
                    "title": "Current Power Draw (kW)",
                    "gridPos": {"h": 8, "w": 6, "x": 0, "y": 2},
                    "targets": [{
                        "format": "table",
                        "rawQuery": True,
                        "query": "SELECT power_w/1000 as power_kw FROM meter_readings WHERE meter_id='auto_factory_001' ORDER BY timestamp DESC LIMIT 1"
                    }],
                    "fieldConfig": {
                        "defaults": {
                            "unit": "short",
                            "color": {"mode": "thresholds"},
                            "thresholds": {
                                "mode": "absolute",
                                "steps": [
                                    {"color": "green", "value": None},
                                    {"color": "yellow", "value": 100},
                                    {"color": "orange", "value": 160},
                                    {"color": "red", "value": 190}
                                ]
                            },
                            "max": 200,
                            "min": 0
                        }
                    }
                },
                # Stats
                {
                    "id": 6,
                    "type": "stat",
                    "title": "Voltage (V)",
                    "gridPos": {"h": 4, "w": 3, "x": 6, "y": 2},
                    "targets": [{
                        "format": "table",
                        "rawQuery": True,
                        "query": "SELECT voltage_v FROM meter_readings WHERE meter_id='auto_factory_001' ORDER BY timestamp DESC LIMIT 1"
                    }],
                    "fieldConfig": {"defaults": {"unit": "volt"}}
                },
                {
                    "id": 7,
                    "type": "stat",
                    "title": "Current (A)",
                    "gridPos": {"h": 4, "w": 3, "x": 9, "y": 2},
                    "targets": [{
                        "format": "table",
                        "rawQuery": True,
                        "query": "SELECT current_a FROM meter_readings WHERE meter_id='auto_factory_001' ORDER BY timestamp DESC LIMIT 1"
                    }],
                    "fieldConfig": {"defaults": {"unit": "amp"}}
                },
                {
                    "id": 8,
                    "type": "stat",
                    "title": "Frequency (Hz)",
                    "gridPos": {"h": 4, "w": 3, "x": 12, "y": 2},
                    "targets": [{
                        "format": "table",
                        "rawQuery": True,
                        "query": "SELECT frequency_hz FROM meter_readings WHERE meter_id='auto_factory_001' ORDER BY timestamp DESC LIMIT 1"
                    }],
                    "fieldConfig": {"defaults": {"unit": "short"}}
                },
                {
                    "id": 9,
                    "type": "stat",
                    "title": "FAULT DETECTED",
                    "gridPos": {"h": 4, "w": 3, "x": 15, "y": 2},
                    "targets": [{
                        "format": "table",
                        "rawQuery": True,
                        "query": "SELECT fault_type FROM meter_readings WHERE meter_id='auto_factory_001' ORDER BY timestamp DESC LIMIT 1"
                    }]
                },
                {
                    "id": 10,
                    "type": "stat",
                    "title": "Latency (ms)",
                    "gridPos": {"h": 4, "w": 3, "x": 18, "y": 2},
                    "targets": [{
                        "format": "table",
                        "rawQuery": True,
                        "query": "SELECT latency_ms FROM meter_readings WHERE meter_id='auto_factory_001' ORDER BY timestamp DESC LIMIT 1"
                    }],
                    "fieldConfig": {"defaults": {"unit": "ms"}}
                },
                {
                    "id": 11,
                    "type": "stat",
                    "title": "AVG LOAD (kW)",
                    "gridPos": {"h": 4, "w": 3, "x": 21, "y": 2},
                    "targets": [{
                        "format": "table",
                        "rawQuery": True,
                        "query": "SELECT AVG(power_w)/1000 as avg_kw FROM meter_readings WHERE meter_id='auto_factory_001' AND timestamp > now() - 3600000"
                    }],
                    "fieldConfig": {"defaults": {"unit": "short"}}
                },
                # Charts
                {
                    "id": 12,
                    "type": "timeseries",
                    "title": "Production Power Load (Last Hour)",
                    "gridPos": {"h": 8, "w": 12, "x": 0, "y": 10},
                    "targets": [{
                        "format": "time_series",
                        "rawQuery": True,
                        "query": "SELECT timestamp, power_w/1000 as power_kw FROM meter_readings WHERE meter_id='auto_factory_001' ORDER BY timestamp DESC LIMIT 3600"
                    }],
                    "fieldConfig": {
                        "defaults": {
                            "custom": {"lineWidth": 2, "fillOpacity": 10},
                            "color": {"mode": "fixed", "fixedColor": "orange"},
                            "unit": "short"
                        }
                    }
                },
                {
                    "id": 13,
                    "type": "timeseries",
                    "title": "Equipment Anomaly Detection",
                    "gridPos": {"h": 8, "w": 12, "x": 12, "y": 10},
                    "targets": [{
                        "format": "time_series",
                        "rawQuery": True,
                        "query": "SELECT timestamp, anomaly_score FROM meter_readings WHERE meter_id='auto_factory_001' ORDER BY timestamp DESC LIMIT 3600"
                    }],
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
                # Critical events
                {
                    "id": 14,
                    "type": "table",
                    "title": "🔴 CRITICAL EVENTS (Maintenance Required)",
                    "gridPos": {"h": 8, "w": 24, "x": 0, "y": 18},
                    "targets": [{
                        "format": "table",
                        "rawQuery": True,
                        "query": "SELECT timestamp, power_w/1000 as power_kw, anomaly_score, current_a, fault_type FROM meter_readings WHERE meter_id='auto_factory_001' AND anomaly_score > 0.7 ORDER BY timestamp DESC LIMIT 25"
                    }]
                }
            ],
            "schemaVersion": 38,
            "style": "dark",
            "templating": {"list": []},
            "annotations": {"list": []}
        },
        "overwrite": True
    }
    
    try:
        response = requests.post(url, json=dashboard, headers=headers, 
                                auth=(GRAFANA_USER, GRAFANA_PASS), timeout=10)
        if response.status_code in [200, 409]:
            print("✅ Factory Dashboard created")
            return True
    except Exception as e:
        print(f"❌ Factory Dashboard: {e}")
    return False

def create_mall_dashboard():
    """SHOPPING MALL MONITOR - 80kW-500kW"""
    
    url = f"{GRAFANA_URL}/api/dashboards/db"
    
    dashboard = {
        "dashboard": {
            "title": "🛍️ SHOPPING MALL MONITOR - Energy Management",
            "description": "Commercial shopping center energy distribution (80kW-500kW)",
            "tags": ["commercial", "shopping", "energy-management"],
            "timezone": "browser",
            "refresh": "1s",
            "time": {"from": "now-1h", "to": "now"},
            "panels": [
                # Header
                {
                    "id": 1,
                    "type": "stat",
                    "title": "FACILITY STATUS",
                    "gridPos": {"h": 2, "w": 6, "x": 0, "y": 0},
                    "targets": [{
                        "format": "table",
                        "rawQuery": True,
                        "query": "SELECT status FROM meter_readings WHERE meter_id='shopping_mall_001' ORDER BY timestamp DESC LIMIT 1"
                    }],
                    "fieldConfig": {"defaults": {"color": {"mode": "fixed", "fixedColor": "purple"}}}
                },
                {
                    "id": 2,
                    "type": "stat",
                    "title": "ANOMALY SCORE",
                    "gridPos": {"h": 2, "w": 6, "x": 6, "y": 0},
                    "targets": [{
                        "format": "table",
                        "rawQuery": True,
                        "query": "SELECT anomaly_score FROM meter_readings WHERE meter_id='shopping_mall_001' ORDER BY timestamp DESC LIMIT 1"
                    }],
                    "fieldConfig": {
                        "defaults": {
                            "unit": "short",
                            "decimals": 3,
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
                {
                    "id": 3,
                    "type": "stat",
                    "title": "SYSTEM HEALTH",
                    "gridPos": {"h": 2, "w": 6, "x": 12, "y": 0},
                    "targets": [{
                        "format": "table",
                        "rawQuery": True,
                        "query": "SELECT risk_level FROM meter_readings WHERE meter_id='shopping_mall_001' ORDER BY timestamp DESC LIMIT 1"
                    }],
                    "fieldConfig": {
                        "defaults": {
                            "mappings": [
                                {"type": "value", "options": {"NORMAL": {"text": "✅", "color": "green"}, "ALERT": {"text": "⚠️", "color": "orange"}}},
                            ]
                        }
                    }
                },
                {
                    "id": 4,
                    "type": "stat",
                    "title": "PEAK LOAD TODAY",
                    "gridPos": {"h": 2, "w": 6, "x": 18, "y": 0},
                    "targets": [{
                        "format": "table",
                        "rawQuery": True,
                        "query": "SELECT MAX(power_w)/1000 as peak_kw FROM meter_readings WHERE meter_id='shopping_mall_001' AND timestamp > now() - 86400000"
                    }],
                    "fieldConfig": {"defaults": {"unit": "short"}}
                },
                # Gauge
                {
                    "id": 5,
                    "type": "gauge",
                    "title": "Current Building Load (kW)",
                    "gridPos": {"h": 8, "w": 6, "x": 0, "y": 2},
                    "targets": [{
                        "format": "table",
                        "rawQuery": True,
                        "query": "SELECT power_w/1000 as power_kw FROM meter_readings WHERE meter_id='shopping_mall_001' ORDER BY timestamp DESC LIMIT 1"
                    }],
                    "fieldConfig": {
                        "defaults": {
                            "unit": "short",
                            "color": {"mode": "thresholds"},
                            "thresholds": {
                                "mode": "absolute",
                                "steps": [
                                    {"color": "green", "value": None},
                                    {"color": "yellow", "value": 200},
                                    {"color": "orange", "value": 350},
                                    {"color": "red", "value": 450}
                                ]
                            },
                            "max": 500,
                            "min": 0
                        }
                    }
                },
                # Stats
                {
                    "id": 6,
                    "type": "stat",
                    "title": "Voltage (V)",
                    "gridPos": {"h": 4, "w": 3, "x": 6, "y": 2},
                    "targets": [{
                        "format": "table",
                        "rawQuery": True,
                        "query": "SELECT voltage_v FROM meter_readings WHERE meter_id='shopping_mall_001' ORDER BY timestamp DESC LIMIT 1"
                    }],
                    "fieldConfig": {"defaults": {"unit": "volt"}}
                },
                {
                    "id": 7,
                    "type": "stat",
                    "title": "Current (A)",
                    "gridPos": {"h": 4, "w": 3, "x": 9, "y": 2},
                    "targets": [{
                        "format": "table",
                        "rawQuery": True,
                        "query": "SELECT current_a FROM meter_readings WHERE meter_id='shopping_mall_001' ORDER BY timestamp DESC LIMIT 1"
                    }],
                    "fieldConfig": {"defaults": {"unit": "amp"}}
                },
                {
                    "id": 8,
                    "type": "stat",
                    "title": "Frequency (Hz)",
                    "gridPos": {"h": 4, "w": 3, "x": 12, "y": 2},
                    "targets": [{
                        "format": "table",
                        "rawQuery": True,
                        "query": "SELECT frequency_hz FROM meter_readings WHERE meter_id='shopping_mall_001' ORDER BY timestamp DESC LIMIT 1"
                    }],
                    "fieldConfig": {"defaults": {"unit": "short"}}
                },
                {
                    "id": 9,
                    "type": "stat",
                    "title": "FAULT",
                    "gridPos": {"h": 4, "w": 3, "x": 15, "y": 2},
                    "targets": [{
                        "format": "table",
                        "rawQuery": True,
                        "query": "SELECT fault_type FROM meter_readings WHERE meter_id='shopping_mall_001' ORDER BY timestamp DESC LIMIT 1"
                    }]
                },
                {
                    "id": 10,
                    "type": "stat",
                    "title": "Latency (ms)",
                    "gridPos": {"h": 4, "w": 3, "x": 18, "y": 2},
                    "targets": [{
                        "format": "table",
                        "rawQuery": True,
                        "query": "SELECT latency_ms FROM meter_readings WHERE meter_id='shopping_mall_001' ORDER BY timestamp DESC LIMIT 1"
                    }],
                    "fieldConfig": {"defaults": {"unit": "ms"}}
                },
                {
                    "id": 11,
                    "type": "stat",
                    "title": "24h AVG (kW)",
                    "gridPos": {"h": 4, "w": 3, "x": 21, "y": 2},
                    "targets": [{
                        "format": "table",
                        "rawQuery": True,
                        "query": "SELECT AVG(power_w)/1000 as avg_kw FROM meter_readings WHERE meter_id='shopping_mall_001' AND timestamp > now() - 86400000"
                    }],
                    "fieldConfig": {"defaults": {"unit": "short"}}
                },
                # Charts
                {
                    "id": 12,
                    "type": "timeseries",
                    "title": "Mall Energy Consumption (Last Hour)",
                    "gridPos": {"h": 8, "w": 12, "x": 0, "y": 10},
                    "targets": [{
                        "format": "time_series",
                        "rawQuery": True,
                        "query": "SELECT timestamp, power_w/1000 as power_kw FROM meter_readings WHERE meter_id='shopping_mall_001' ORDER BY timestamp DESC LIMIT 3600"
                    }],
                    "fieldConfig": {
                        "defaults": {
                            "custom": {"lineWidth": 2, "fillOpacity": 10},
                            "color": {"mode": "fixed", "fixedColor": "purple"},
                            "unit": "short"
                        }
                    }
                },
                {
                    "id": 13,
                    "type": "timeseries",
                    "title": "System Stability Index",
                    "gridPos": {"h": 8, "w": 12, "x": 12, "y": 10},
                    "targets": [{
                        "format": "time_series",
                        "rawQuery": True,
                        "query": "SELECT timestamp, anomaly_score FROM meter_readings WHERE meter_id='shopping_mall_001' ORDER BY timestamp DESC LIMIT 3600"
                    }],
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
                # Issues
                {
                    "id": 14,
                    "type": "table",
                    "title": "⚠️ Energy Anomalies (Last 24 Hours)",
                    "gridPos": {"h": 8, "w": 24, "x": 0, "y": 18},
                    "targets": [{
                        "format": "table",
                        "rawQuery": True,
                        "query": "SELECT timestamp, power_w/1000 as power_kw, anomaly_score, voltage_v, current_a FROM meter_readings WHERE meter_id='shopping_mall_001' AND anomaly_score > 0.3 ORDER BY timestamp DESC LIMIT 25"
                    }]
                }
            ],
            "schemaVersion": 38,
            "style": "dark",
            "templating": {"list": []},
            "annotations": {"list": []}
        },
        "overwrite": True
    }
    
    try:
        response = requests.post(url, json=dashboard, headers=headers, 
                                auth=(GRAFANA_USER, GRAFANA_PASS), timeout=10)
        if response.status_code in [200, 409]:
            print("✅ Shopping Mall Dashboard created")
            return True
    except Exception as e:
        print(f"❌ Mall Dashboard: {e}")
    return False

def create_textile_dashboard():
    """TEXTILE MILL MONITOR - 100kW-250kW"""
    
    url = f"{GRAFANA_URL}/api/dashboards/db"
    
    dashboard = {
        "dashboard": {
            "title": "🏪 TEXTILE MILL MONITOR - Production Cycles",
            "description": "Textile processing with cyclic production patterns (100kW-250kW)",
            "tags": ["industrial", "textile", "cycles"],
            "timezone": "browser",
            "refresh": "1s",
            "time": {"from": "now-1h", "to": "now"},
            "panels": [
                # Header
                {
                    "id": 1,
                    "type": "stat",
                    "title": "PRODUCTION STATUS",
                    "gridPos": {"h": 2, "w": 6, "x": 0, "y": 0},
                    "targets": [{
                        "format": "table",
                        "rawQuery": True,
                        "query": "SELECT status FROM meter_readings WHERE meter_id='textile_mill_001' ORDER BY timestamp DESC LIMIT 1"
                    }],
                    "fieldConfig": {"defaults": {"color": {"mode": "fixed", "fixedColor": "red"}}}
                },
                {
                    "id": 2,
                    "type": "stat",
                    "title": "ANOMALY SCORE",
                    "gridPos": {"h": 2, "w": 6, "x": 6, "y": 0},
                    "targets": [{
                        "format": "table",
                        "rawQuery": True,
                        "query": "SELECT anomaly_score FROM meter_readings WHERE meter_id='textile_mill_001' ORDER BY timestamp DESC LIMIT 1"
                    }],
                    "fieldConfig": {
                        "defaults": {
                            "unit": "short",
                            "decimals": 3,
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
                {
                    "id": 3,
                    "type": "stat",
                    "title": "CYCLE STATUS",
                    "gridPos": {"h": 2, "w": 6, "x": 12, "y": 0},
                    "targets": [{
                        "format": "table",
                        "rawQuery": True,
                        "query": "SELECT risk_level FROM meter_readings WHERE meter_id='textile_mill_001' ORDER BY timestamp DESC LIMIT 1"
                    }],
                    "fieldConfig": {
                        "defaults": {
                            "mappings": [
                                {"type": "value", "options": {"NORMAL": {"text": "RUNNING ✅", "color": "green"}, "ALERT": {"text": "⚠️", "color": "orange"}}}
                            ]
                        }
                    }
                },
                {
                    "id": 4,
                    "type": "stat",
                    "title": "PEAK TODAY",
                    "gridPos": {"h": 2, "w": 6, "x": 18, "y": 0},
                    "targets": [{
                        "format": "table",
                        "rawQuery": True,
                        "query": "SELECT MAX(power_w)/1000 as peak_kw FROM meter_readings WHERE meter_id='textile_mill_001' AND timestamp > now() - 86400000"
                    }],
                    "fieldConfig": {"defaults": {"unit": "short"}}
                },
                # Gauge
                {
                    "id": 5,
                    "type": "gauge",
                    "title": "Current Cycle Power (kW)",
                    "gridPos": {"h": 8, "w": 6, "x": 0, "y": 2},
                    "targets": [{
                        "format": "table",
                        "rawQuery": True,
                        "query": "SELECT power_w/1000 as power_kw FROM meter_readings WHERE meter_id='textile_mill_001' ORDER BY timestamp DESC LIMIT 1"
                    }],
                    "fieldConfig": {
                        "defaults": {
                            "unit": "short",
                            "color": {"mode": "thresholds"},
                            "thresholds": {
                                "mode": "absolute",
                                "steps": [
                                    {"color": "green", "value": None},
                                    {"color": "yellow", "value": 120},
                                    {"color": "orange", "value": 200},
                                    {"color": "red", "value": 240}
                                ]
                            },
                            "max": 250,
                            "min": 0
                        }
                    }
                },
                # Stats
                {
                    "id": 6,
                    "type": "stat",
                    "title": "Voltage (V)",
                    "gridPos": {"h": 4, "w": 3, "x": 6, "y": 2},
                    "targets": [{
                        "format": "table",
                        "rawQuery": True,
                        "query": "SELECT voltage_v FROM meter_readings WHERE meter_id='textile_mill_001' ORDER BY timestamp DESC LIMIT 1"
                    }],
                    "fieldConfig": {"defaults": {"unit": "volt"}}
                },
                {
                    "id": 7,
                    "type": "stat",
                    "title": "Current (A)",
                    "gridPos": {"h": 4, "w": 3, "x": 9, "y": 2},
                    "targets": [{
                        "format": "table",
                        "rawQuery": True,
                        "query": "SELECT current_a FROM meter_readings WHERE meter_id='textile_mill_001' ORDER BY timestamp DESC LIMIT 1"
                    }],
                    "fieldConfig": {"defaults": {"unit": "amp"}}
                },
                {
                    "id": 8,
                    "type": "stat",
                    "title": "Frequency (Hz)",
                    "gridPos": {"h": 4, "w": 3, "x": 12, "y": 2},
                    "targets": [{
                        "format": "table",
                        "rawQuery": True,
                        "query": "SELECT frequency_hz FROM meter_readings WHERE meter_id='textile_mill_001' ORDER BY timestamp DESC LIMIT 1"
                    }],
                    "fieldConfig": {"defaults": {"unit": "short"}}
                },
                {
                    "id": 9,
                    "type": "stat",
                    "title": "FAULT",
                    "gridPos": {"h": 4, "w": 3, "x": 15, "y": 2},
                    "targets": [{
                        "format": "table",
                        "rawQuery": True,
                        "query": "SELECT fault_type FROM meter_readings WHERE meter_id='textile_mill_001' ORDER BY timestamp DESC LIMIT 1"
                    }]
                },
                {
                    "id": 10,
                    "type": "stat",
                    "title": "Latency (ms)",
                    "gridPos": {"h": 4, "w": 3, "x": 18, "y": 2},
                    "targets": [{
                        "format": "table",
                        "rawQuery": True,
                        "query": "SELECT latency_ms FROM meter_readings WHERE meter_id='textile_mill_001' ORDER BY timestamp DESC LIMIT 1"
                    }],
                    "fieldConfig": {"defaults": {"unit": "ms"}}
                },
                {
                    "id": 11,
                    "type": "stat",
                    "title": "24h AVG (kW)",
                    "gridPos": {"h": 4, "w": 3, "x": 21, "y": 2},
                    "targets": [{
                        "format": "table",
                        "rawQuery": True,
                        "query": "SELECT AVG(power_w)/1000 as avg_kw FROM meter_readings WHERE meter_id='textile_mill_001' AND timestamp > now() - 86400000"
                    }],
                    "fieldConfig": {"defaults": {"unit": "short"}}
                },
                # Charts
                {
                    "id": 12,
                    "type": "timeseries",
                    "title": "Production Cycle Pattern (Last Hour)",
                    "gridPos": {"h": 8, "w": 12, "x": 0, "y": 10},
                    "targets": [{
                        "format": "time_series",
                        "rawQuery": True,
                        "query": "SELECT timestamp, power_w/1000 as power_kw FROM meter_readings WHERE meter_id='textile_mill_001' ORDER BY timestamp DESC LIMIT 3600"
                    }],
                    "fieldConfig": {
                        "defaults": {
                            "custom": {"lineWidth": 2, "fillOpacity": 10},
                            "color": {"mode": "fixed", "fixedColor": "red"},
                            "unit": "short"
                        }
                    }
                },
                {
                    "id": 13,
                    "type": "timeseries",
                    "title": "Cycle Stability",
                    "gridPos": {"h": 8, "w": 12, "x": 12, "y": 10},
                    "targets": [{
                        "format": "time_series",
                        "rawQuery": True,
                        "query": "SELECT timestamp, anomaly_score FROM meter_readings WHERE meter_id='textile_mill_001' ORDER BY timestamp DESC LIMIT 3600"
                    }],
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
                # Events
                {
                    "id": 14,
                    "type": "table",
                    "title": "⚠️ Cycle Anomalies (Last 24 Hours)",
                    "gridPos": {"h": 8, "w": 24, "x": 0, "y": 18},
                    "targets": [{
                        "format": "table",
                        "rawQuery": True,
                        "query": "SELECT timestamp, power_w/1000 as power_kw, anomaly_score, current_a, fault_type FROM meter_readings WHERE meter_id='textile_mill_001' AND anomaly_score > 0.3 ORDER BY timestamp DESC LIMIT 25"
                    }]
                }
            ],
            "schemaVersion": 38,
            "style": "dark",
            "templating": {"list": []},
            "annotations": {"list": []}
        },
        "overwrite": True
    }
    
    try:
        response = requests.post(url, json=dashboard, headers=headers, 
                                auth=(GRAFANA_USER, GRAFANA_PASS), timeout=10)
        if response.status_code in [200, 409]:
            print("✅ Textile Mill Dashboard created")
            return True
    except Exception as e:
        print(f"❌ Textile Dashboard: {e}")
    return False

def create_master_dashboard():
    """MASTER DASHBOARD - All 5 Meters Overview"""
    
    url = f"{GRAFANA_URL}/api/dashboards/db"
    
    dashboard = {
        "dashboard": {
            "title": "🌍 MASTER CONTROL - System Overview (All 5 Meters)",
            "description": "Real-time system-wide energy monitoring and threat detection",
            "tags": ["master", "overview", "system"],
            "timezone": "browser",
            "refresh": "1s",
            "time": {"from": "now-1h", "to": "now"},
            "panels": [
                # Summary Stats
                {
                    "id": 1,
                    "type": "stat",
                    "title": "📊 Total Meters Online",
                    "gridPos": {"h": 3, "w": 4, "x": 0, "y": 0},
                    "targets": [{
                        "format": "table",
                        "rawQuery": True,
                        "query": "SELECT COUNT(DISTINCT meter_id) as meters_online FROM meter_readings WHERE timestamp > now() - 300000"
                    }],
                    "fieldConfig": {
                        "defaults": {
                            "color": {"mode": "fixed", "fixedColor": "green"},
                            "thresholds": {"mode": "absolute", "steps": [{"color": "green", "value": None}]}
                        }
                    }
                },
                {
                    "id": 2,
                    "type": "stat",
                    "title": "🔴 CRITICAL Alerts",
                    "gridPos": {"h": 3, "w": 4, "x": 4, "y": 0},
                    "targets": [{
                        "format": "table",
                        "rawQuery": True,
                        "query": "SELECT COUNT(*) as critical_count FROM meter_readings WHERE risk_level = 'CRITICAL' AND timestamp > now() - 3600000"
                    }],
                    "fieldConfig": {
                        "defaults": {
                            "color": {"mode": "fixed", "fixedColor": "red"}
                        }
                    }
                },
                {
                    "id": 3,
                    "type": "stat",
                    "title": "⚠️ ALERT Events",
                    "gridPos": {"h": 3, "w": 4, "x": 8, "y": 0},
                    "targets": [{
                        "format": "table",
                        "rawQuery": True,
                        "query": "SELECT COUNT(*) as alert_count FROM meter_readings WHERE risk_level = 'ALERT' AND timestamp > now() - 3600000"
                    }],
                    "fieldConfig": {
                        "defaults": {
                            "color": {"mode": "fixed", "fixedColor": "yellow"}
                        }
                    }
                },
                {
                    "id": 4,
                    "type": "stat",
                    "title": "💾 Total Records",
                    "gridPos": {"h": 3, "w": 4, "x": 12, "y": 0},
                    "targets": [{
                        "format": "table",
                        "rawQuery": True,
                        "query": "SELECT COUNT(*) as total_records FROM meter_readings"
                    }]
                },
                {
                    "id": 5,
                    "type": "stat",
                    "title": "⚡ System Uptime",
                    "gridPos": {"h": 3, "w": 4, "x": 16, "y": 0},
                    "targets": [{
                        "format": "table",
                        "rawQuery": True,
                        "query": "SELECT (now() - MIN(timestamp))/1000 as uptime_seconds FROM meter_readings"
                    }]
                },
                {
                    "id": 6,
                    "type": "stat",
                    "title": "📈 Avg Anomaly Rate",
                    "gridPos": {"h": 3, "w": 4, "x": 20, "y": 0},
                    "targets": [{
                        "format": "table",
                        "rawQuery": True,
                        "query": "SELECT AVG(anomaly_score) as avg_anomaly FROM meter_readings WHERE timestamp > now() - 3600000"
                    }]
                },
                # All Meters Power
                {
                    "id": 7,
                    "type": "timeseries",
                    "title": "🔌 All Meters - Power Consumption Live",
                    "gridPos": {"h": 10, "w": 24, "x": 0, "y": 3},
                    "targets": [{
                        "format": "time_series",
                        "rawQuery": True,
                        "query": "SELECT timestamp, meter_id, power_w FROM meter_readings WHERE timestamp > now() - 3600000 ORDER BY timestamp DESC"
                    }],
                    "fieldConfig": {
                        "defaults": {
                            "custom": {"lineWidth": 2},
                            "unit": "watt"
                        }
                    }
                },
                # All Meters Anomaly
                {
                    "id": 8,
                    "type": "timeseries",
                    "title": "🚨 All Meters - Anomaly Scores",
                    "gridPos": {"h": 10, "w": 24, "x": 0, "y": 13},
                    "targets": [{
                        "format": "time_series",
                        "rawQuery": True,
                        "query": "SELECT timestamp, meter_id, anomaly_score FROM meter_readings WHERE timestamp > now() - 3600000 ORDER BY timestamp DESC"
                    }],
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
                # Meter Comparison Table
                {
                    "id": 9,
                    "type": "table",
                    "title": "📊 5-Meter Status Comparison (Last Update)",
                    "gridPos": {"h": 10, "w": 24, "x": 0, "y": 23},
                    "targets": [{
                        "format": "table",
                        "rawQuery": True,
                        "query": "SELECT meter_id, power_w, anomaly_score, voltage_v, current_a, risk_level, timestamp FROM (SELECT meter_id, power_w, anomaly_score, voltage_v, current_a, risk_level, timestamp, ROW_NUMBER() OVER (PARTITION BY meter_id ORDER BY timestamp DESC) as rn FROM meter_readings) WHERE rn = 1 ORDER BY meter_id"
                    }]
                }
            ],
            "schemaVersion": 38,
            "style": "dark",
            "templating": {"list": []},
            "annotations": {"list": []}
        },
        "overwrite": True
    }
    
    try:
        response = requests.post(url, json=dashboard, headers=headers, 
                                auth=(GRAFANA_USER, GRAFANA_PASS), timeout=10)
        if response.status_code in [200, 409]:
            print("✅ Master Control Dashboard created")
            return True
    except Exception as e:
        print(f"❌ Master Dashboard: {e}")
    return False

if __name__ == "__main__":
    print("\n" + "="*70)
    print(" 🎯 PROFESSIONAL GRAFANA DASHBOARDS - PRODUCTION DEPLOYMENT")
    print("="*70)
    print("\n[DEPLOYING] Initializing dashboard setup...\n")
    
    setup_datasource()
    time.sleep(1)
    
    # Create all dashboards
    results = [
        create_apartment_dashboard(),
        create_suburban_dashboard(),
        create_factory_dashboard(),
        create_mall_dashboard(),
        create_textile_dashboard(),
        create_master_dashboard()
    ]
    
    print("\n" + "="*70)
    print(" ✅ DASHBOARD DEPLOYMENT COMPLETE")
    print("="*70)
    print(f"\n✅ Total Dashboards Created: {sum(results)}/6")
    print("\n🌐 ACCESS YOUR DASHBOARDS:")
    print("   URL: http://localhost:3000")
    print("   Login: admin / admin")
    print("\n📊 DASHBOARD LIST:")
    print("   1. 🏠 Apartment Monitor")
    print("   2. 🏡 Suburban Home Monitor")
    print("   3. 🏭 Automobile Factory Monitor")
    print("   4. 🛍️ Shopping Mall Monitor")
    print("   5. 🏪 Textile Mill Monitor")
    print("   6. 🌍 Master Control (System Overview)")
    print("\n⚙️  CONFIGURATION:")
    print("   • Refresh Rate: 1 second (LIVE UPDATES)")
    print("   • Color Coding: Green ✅ Yellow ⚠️ Orange ⚠️ Red 🔴")
    print("   • Data Range: Last 1 hour")
    print("   • Theme: Professional Dark Mode")
    print("\n" + "="*70 + "\n")
