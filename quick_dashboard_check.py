#!/usr/bin/env python
import requests
import time
import json

GRAFANA_URL = "http://localhost:3000"
GRAFANA_USER = "admin"
GRAFANA_PASS = "admin"

def check_dashboards():
    """Check if dashboards exist"""
    try:
        # Query Grafana API
        response = requests.get(
            f"{GRAFANA_URL}/api/search?type=dash-db",
            auth=(GRAFANA_USER, GRAFANA_PASS),
            timeout=5
        )
        
        if response.status_code == 200:
            dashboards = response.json()
            print(f"\n✅ Found {len(dashboards)} dashboards:\n")
            for dash in dashboards:
                print(f"   • {dash['title']}")
            return dashboards
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return []

if __name__ == "__main__":
    print("=" * 70)
    print("🔍 CHECKING GRAFANA DASHBOARDS")
    print("=" * 70)
    
    dashboards = check_dashboards()
    
    if not dashboards:
        print("\n⚠️  No dashboards found!")
        print("\n💡 To create dashboards, run:")
        print("   python create_professional_dashboards.py")
    else:
        print(f"\n✅ All dashboards are ready!")
        print("\n🌐 Open Grafana: http://localhost:3000")
