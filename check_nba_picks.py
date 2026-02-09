#!/usr/bin/env python3
"""
Check if NBA picks are available
"""
import requests

def check_nba_picks():
    """Check if NBA picks are available"""
    base_url = "https://railway-engine-production.up.railway.app"
    
    print("CHECKING NBA PICKS AVAILABILITY")
    print("="*80)
    
    # Check player props for NBA
    url = f"{base_url}/api/sports/30/picks/player-props?limit=10"
    
    try:
        response = requests.get(url, timeout=10)
        print(f"\nPlayer Props Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"  Found {len(data.get('items', []))} player props")
            if data.get('items'):
                print(f"  Sample: {data['items'][0].get('player', 'N/A')}")
        else:
            print("  No player props found")
    except Exception as e:
        print(f"  Error: {e}")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    check_nba_picks()
