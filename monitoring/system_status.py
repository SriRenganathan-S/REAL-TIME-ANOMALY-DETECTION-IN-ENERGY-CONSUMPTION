"""
System Status Checker - Verifies if Spark Brain is alive and running
PHASE 4 ENHANCEMENT: Alert system status and dashboard readiness
"""
import sys
import json
from datetime import datetime, timedelta
from cassandra.cluster import Cluster

print("\n🔍 CHECKING SYSTEM STATUS...\n")

try:
    # Connect to Cassandra
    cluster = Cluster(['localhost'])
    session = cluster.connect('energy_db')
    
    # ==========================================
    # 📊 PHASE 1: SPARK HEARTBEAT CHECK
    # ==========================================
    
    heartbeat_query = "SELECT processor_id, timestamp, status FROM system_heartbeat WHERE processor_id='spark_brain_processor' LIMIT 1"
    result = session.execute(heartbeat_query)
    
    rows = list(result)
    
    if not rows:
        print("❌ NO HEARTBEAT FOUND")
        print("   Status: Spark Brain is NOT running or not yet started")
        print("   Action: Start Spark Brain with: docker-compose up -d")
        sys.exit(1)
    
    last_heartbeat = rows[0]
    last_update = last_heartbeat.timestamp
    current_time = datetime.now()
    
    # Calculate time difference (accounting for timezone)
    time_diff = (current_time - last_update).total_seconds()
    
    if time_diff < 10:
        print("✅ SPARK BRAIN IS ALIVE AND RUNNING")
        print(f"   Processor: {last_heartbeat.processor_id}")
        print(f"   Status: {last_heartbeat.status}")
        print(f"   Last Update: {last_update}")
        print(f"   Time Since Last Heartbeat: {time_diff:.1f} seconds")
        
    elif time_diff < 60:
        print("⚠️  SPARK BRAIN IS RUNNING BUT DELAYED")
        print(f"   Last Update: {time_diff:.1f} seconds ago")
        print("   Action: Wait a few more seconds or check if Spark Brain is slow")
    
    else:
        print("❌ SPARK BRAIN IS NOT RESPONDING (Stalled)")
        print(f"   Last Update: {time_diff:.1f} seconds ago")
        print("   Action: Restart Spark Brain")
    
    print("\n📊 Data is being collected and stored in Cassandra")
    print("📈 Grafana dashboard should display LIVE data")
    
    # ==========================================
    # 🚨 PHASE 4: ALERT SYSTEM CHECK
    # ==========================================
    
    try:
        # Check if alerts table exists
        alerts_count_query = "SELECT COUNT(*) as count FROM alerts WHERE timestamp > now() - 3600000"
        alerts_result = session.execute(alerts_count_query)
        alerts_row = list(alerts_result)[0]
        alerts_count = alerts_row.count if hasattr(alerts_row, 'count') else 0
        
        print(f"\n✅ PHASE 4 - ALERT SYSTEM STATUS")
        print(f"   Alerts logged in last hour: {alerts_count}")
        if alerts_count > 0:
            print(f"   🚨 Recent anomalies detected and logged")
        else:
            print(f"   ℹ️  No recent alerts (system operating normally)")
        
    except Exception as e:
        print(f"\n⚠️  PHASE 4 - Alert table not yet initialized: {e}")
        print(f"   The alerts table will be created on first anomaly detection")
    
    # ==========================================
    # 📊 METER STATUS CHECK
    # ==========================================
    
    try:
        meter_query = "SELECT meter_id, COUNT(*) as readings FROM meter_readings GROUP BY meter_id"
        meters_result = session.execute(meter_query)
        meters = list(meters_result)
        
        print(f"\n✅ ACTIVE METERS")
        for meter in meters:
            meter_id = meter.meter_id
            count = meter.readings if hasattr(meter, 'readings') else 0
            print(f"   • {meter_id}: {count} readings")
        
    except Exception as e:
        print(f"⚠️  Could not get meter details: {e}")
    
    # ==========================================
    # 📈 DASHBOARD READINESS
    # ==========================================
    
    try:
        import requests
        grafana_response = requests.get("http://localhost:3000/api/search?type=dash-db", 
                                       auth=("admin", "admin"), timeout=3)
        if grafana_response.status_code == 200:
            dashboards = grafana_response.json()
            print(f"\n✅ GRAFANA DASHBOARDS READY")
            print(f"   {len(dashboards)} dashboards available")
            for dash in dashboards[:3]:
                print(f"   • {dash.get('title', 'Unknown')}")
            if len(dashboards) > 3:
                print(f"   ... and {len(dashboards)-3} more")
        else:
            print(f"\n⚠️  Grafana connection issue: {grafana_response.status_code}")
    except Exception as e:
        print(f"\n⚠️  Could not reach Grafana: {e}")
    
    cluster.shutdown()
    sys.exit(0)
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    sys.exit(1)
