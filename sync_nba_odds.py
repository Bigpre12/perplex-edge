#!/usr/bin/env python3
"""
Sync NBA odds with correct sport name
"""
import requests

def sync_nba_odds():
    """Sync NBA odds"""
    base_url = "https://railway-engine-production.up.railway.app"
    
    print("SYNCING NBA ODDS")
    print("="*80)
    
    # Sync NBA odds using sport name
    print("\n1. Sync NBA Odds:")
    sync_url = f"{base_url}/api/sync/odds/NBA"
    
    try:
        response = requests.post(sync_url, timeout=30)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Sync result: {data}")
        else:
            print(f"   Error: {response.text[:100]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Check odds after sync
    print("\n2. Check NBA Odds After Sync:")
    nba_odds_url = f"{base_url}/api/data/v2/odds/nba"
    
    try:
        response = requests.get(nba_odds_url, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            count = data.get('count', 0)
            print(f"   NBA odds count: {count}")
            
            if count > 0:
                odds_data = data.get('data', [])
                print(f"   Sample odds:")
                for odd in odds_data[:3]:
                    print(f"     - {odd}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    sync_nba_odds()
