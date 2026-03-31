"""
CLEANUP OLD DASHBOARDS - Keep only the 6 professional dashboards
"""

import requests
import json

GRAFANA_URL = "http://localhost:3000"
GRAFANA_USER = "admin"
GRAFANA_PASS = "admin"

headers = {
    "Authorization": f"Bearer admin",
    "Content-Type": "application/json"
}

# Dashboards to KEEP (the ones we just created)
KEEP_DASHBOARDS = [
    "APARTMENT MONITOR - Real-Time Energy",
    "SUBURBAN HOME MONITOR - Smart Living",
    "AUTOMOBILE FACTORY MONITOR - Production Control",
    "SHOPPING MALL MONITOR - Energy Management",
    "TEXTILE MILL MONITOR - Production Cycles",
    "MASTER CONTROL - System Overview (All 5 Meters)"
]

def get_all_dashboards():
    """Get all dashboards from Grafana"""
    url = f"{GRAFANA_URL}/api/search?type=dash-db"
    try:
        response = requests.get(url, headers=headers, auth=(GRAFANA_USER, GRAFANA_PASS), timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"❌ Error fetching dashboards: {e}")
    return []

def delete_dashboard(dashboard_id):
    """Delete a dashboard by ID"""
    url = f"{GRAFANA_URL}/api/dashboards/uid/{dashboard_id}"
    try:
        response = requests.delete(url, headers=headers, auth=(GRAFANA_USER, GRAFANA_PASS), timeout=10)
        if response.status_code in [200, 204]:
            return True
    except Exception as e:
        print(f"❌ Error deleting dashboard: {e}")
    return False

if __name__ == "__main__":
    print("\n" + "="*70)
    print(" 🧹 CLEANING UP OLD DASHBOARDS")
    print("="*70 + "\n")
    
    dashboards = get_all_dashboards()
    print(f"📊 Found {len(dashboards)} total dashboards\n")
    
    deleted_count = 0
    kept_count = 0
    
    for dash in dashboards:
        dash_title = dash.get('title', 'Unknown')
        dash_id = dash.get('uid', '')
        
        # Check if this dashboard should be kept
        should_keep = any(keep_name in dash_title for keep_name in KEEP_DASHBOARDS)
        
        if should_keep:
            print(f"✅ KEEP: {dash_title}")
            kept_count += 1
        else:
            print(f"🗑️  DELETE: {dash_title}")
            if delete_dashboard(dash_id):
                print(f"   ✅ Deleted successfully")
                deleted_count += 1
            else:
                print(f"   ⚠️  Failed to delete")
    
    print("\n" + "="*70)
    print(f" ✅ CLEANUP COMPLETE")
    print("="*70)
    print(f"\n📊 Kept {kept_count} professional dashboards")
    print(f"🗑️  Deleted {deleted_count} old/duplicate dashboards")
    print("\n🌐 Your dashboards are now clean!")
    print(f"   URL: http://localhost:3000")
    print("\n" + "="*70 + "\n")
