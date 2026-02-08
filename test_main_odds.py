#!/usr/bin/env python3
"""
Test main odds endpoints
"""
import requests

def test_main_odds():
    """Test main odds endpoints"""
    base_url = "https://railway-engine-production.up.railway.app"
    
    print("TESTING MAIN ODDS ENDPOINTS")
    print("="*80)
    
    endpoints = [
        ("/api/odds", "Main odds"),
        ("/api/odds/best", "Best odds"),
        ("/api/nfl/odds", "NFL odds"),
        ("/api/ncaab/odds", "NCAAB odds"),
    ]
    
    for endpoint, desc in endpoints:
        url = base_url + endpoint
        print(f"\n{desc}: {endpoint}")
        
        try:
            response = requests.get(url, timeout=10)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict):
                    print(f"   Keys: {list(data.keys())[:5]}")
                elif isinstance(data, list):
                    print(f"   List with {len(data)} items")
                    if data:
                        print(f"   Sample: {data[0]}")
            else:
                print(f"   Error: {response.text[:100]}")
        except Exception as e:
            print(f"   Error: {e}")
    
    # Try to sync odds for NBA
    print("\nSync NBA Odds:")
    sync_url = f"{base_url}/api/sync/odds/30"
    
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
    
    print("\n" + "="*80)

if __name__ == "__main__":
    test_main_odds()
