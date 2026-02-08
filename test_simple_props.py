#!/usr/bin/env python3
"""
Test simple props query
"""
import requests

def test_simple_props():
    """Test simple props query"""
    base_url = "https://railway-engine-production.up.railway.app"
    
    print("TESTING SIMPLE PROPS QUERY")
    print("="*80)
    
    # Try to get props without complex filters
    print("\n1. Simple Props Query:")
    props_url = f"{base_url}/api/sports/31/picks/player-props?limit=10"
    
    try:
        response = requests.get(props_url, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            props = data.get('items', [])
            print(f"   Found {len(props)} props")
            
            if props:
                for prop in props[:3]:
                    player = prop.get('player', {})
                    print(f"   - {player.get('name', 'N/A')}: {prop.get('stat_type', 'N/A')} {prop.get('line_value', 'N/A')}")
                    print(f"     Edge: {prop.get('edge', 0):.2%}")
            else:
                print("   No props found")
        else:
            print(f"   Error: {response.text[:200]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Try to get all picks
    print("\n2. All Picks Query:")
    all_picks_url = f"{base_url}/api/sports/31/picks?limit=10"
    
    try:
        response = requests.get(all_picks_url, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            picks = data.get('items', [])
            print(f"   Found {len(picks)} picks")
            
            if picks:
                for pick in picks[:3]:
                    player = pick.get('player', {})
                    print(f"   - {player.get('name', 'N/A')}: {pick.get('stat_type', 'N/A')} {pick.get('line_value', 'N/A')}")
                    print(f"     Edge: {pick.get('edge', 0):.2%}")
            else:
                print("   No picks found")
        else:
            print(f"   Error: {response.text[:200]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Check if the picks endpoint exists at all
    print("\n3. Check Picks Endpoint:")
    picks_endpoint_url = f"{base_url}/api/picks?sport_id=31&limit=10"
    
    try:
        response = requests.get(picks_endpoint_url, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Picks endpoint working: {data}")
        else:
            print(f"   Error: {response.text[:100]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    test_simple_props()
