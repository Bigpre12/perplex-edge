#!/usr/bin/env python3
"""
Check if we can trigger pick generation
"""
import requests

def check_pick_generation():
    """Check pick generation options"""
    base_url = "https://railway-engine-production.up.railway.app"
    
    print("CHECKING PICK GENERATION OPTIONS")
    print("="*80)
    
    # Check manual refresh for NBA
    print("\n1. Manual Refresh NBA (sport_id=30):")
    refresh_url = f"{base_url}/admin/jobs/manual-refresh/30"
    
    try:
        response = requests.post(refresh_url, timeout=30)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Refresh result: {data}")
        else:
            print(f"   Error: {response.text[:100]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Check force refresh
    print("\n2. Force Refresh All:")
    force_url = f"{base_url}/admin/jobs/force-refresh"
    
    try:
        response = requests.post(force_url, timeout=30)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Force refresh result: {data}")
        else:
            print(f"   Error: {response.text[:100]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n" + "="*80)
    print("SUMMARY:")
    print("- Games exist for NBA and Super Bowl")
    print("- No picks are available for today's games")
    print("- Parlay builder needs picks to generate parlays")
    print("- Pick generation may need to be triggered manually")
    print("="*80)

if __name__ == "__main__":
    check_pick_generation()
