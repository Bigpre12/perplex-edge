#!/usr/bin/env python3
"""
Check if data needs to be synced
"""
import requests

def check_data_sync():
    """Check if data needs syncing"""
    base_url = "https://railway-engine-production.up.railway.app"
    
    print("CHECKING DATA SYNC STATUS")
    print("="*80)
    
    # Check admin season info
    print("\n1. Admin Season Info:")
    season_url = f"{base_url}/api/admin/season-info"
    
    try:
        response = requests.get(season_url, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Status: {data.get('status', 'N/A')}")
            print(f"   Current Date: {data.get('current_date', 'N/A')}")
            
            sports = data.get('sports', {})
            for sport_id, sport_data in sports.items():
                if sport_id in ['30', '31']:  # NBA and NFL
                    print(f"   {sport_data.get('name', 'N/A')}: {sport_data.get('status', 'N/A')}")
        else:
            print(f"   Error: {response.text[:100]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Check if there are any recent sync jobs
    print("\n2. Check Sync Status:")
    sync_status_url = f"{base_url}/api/admin/jobs/sync-quota-safe"
    
    try:
        response = requests.post(sync_status_url, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Sync triggered: {data.get('message', 'N/A')}")
        else:
            print(f"   Error: {response.text[:100]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n" + "="*80)
    print("NOTE: No picks available means the model hasn't generated predictions")
    print("for today's games. The parlay builder needs picks to create parlays.")
    print("="*80)

if __name__ == "__main__":
    check_data_sync()
