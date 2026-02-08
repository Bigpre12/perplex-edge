#!/usr/bin/env python3
"""
Check player props for NBA and NFL games today
"""
import requests

def check_player_props():
    """Check player props for NBA and NFL"""
    base_url = "https://railway-engine-production.up.railway.app"
    
    print("CHECKING PLAYER PROPS FOR TODAY'S GAMES")
    print("="*80)
    
    # Check NBA player props
    print("\n1. NBA Player Props (sport_id=30):")
    nba_url = f"{base_url}/api/sports/30/picks/player-props?limit=20"
    
    try:
        response = requests.get(nba_url, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            props = data.get('items', [])
            print(f"   Found {len(props)} NBA player props")
            
            if props:
                print("   Sample props:")
                for prop in props[:3]:
                    print(f"   - {prop.get('player', {}).get('name', 'N/A')}: {prop.get('stat_type', 'N/A')} {prop.get('line_value', 'N/A')} ({prop.get('side', 'N/A')})")
                    print(f"     Edge: {prop.get('edge', 'N/A'):.2%}")
        else:
            print(f"   Error: {response.text[:100]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Check NFL player props
    print("\n2. NFL Player Props (sport_id=31):")
    nfl_url = f"{base_url}/api/sports/31/picks/player-props?limit=20"
    
    try:
        response = requests.get(nfl_url, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            props = data.get('items', [])
            print(f"   Found {len(props)} NFL player props")
            
            if props:
                print("   Sample props:")
                for prop in props[:3]:
                    print(f"   - {prop.get('player', {}).get('name', 'N/A')}: {prop.get('stat_type', 'N/A')} {prop.get('line_value', 'N/A')} ({prop.get('side', 'N/A')})")
                    print(f"     Edge: {prop.get('edge', 'N/A'):.2%}")
        else:
            print(f"   Error: {response.text[:100]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    check_player_props()
