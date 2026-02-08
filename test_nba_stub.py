#!/usr/bin/env python3
"""
Test NBA stub props
"""
import requests

def test_nba_stub():
    """Test NBA stub props"""
    base_url = "https://railway-engine-production.up.railway.app"
    
    print("TESTING NBA STUB PROPS")
    print("="*80)
    
    # Test NBA stub props
    print("\n1. NBA Stub Props:")
    stub_url = f"{base_url}/api/sports/30/picks/player-props-stub"
    
    try:
        response = requests.get(stub_url, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            props = data.get('items', [])
            print(f"   Found {len(props)} NBA stub props")
            
            if props:
                print(f"   Sample props:")
                for prop in props[:5]:
                    player = prop.get('player', {})
                    print(f"   - {player.get('name', 'N/A')}: {prop.get('stat_type', 'N/A')} {prop.get('line_value', 'N/A')} ({prop.get('side', 'N/A')})")
                    print(f"     Edge: {prop.get('edge', 0):.2%}")
            else:
                print("   No NBA stub props (only NFL)")
        else:
            print(f"   Error: {response.text[:100]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test NBA parlay builder
    print("\n2. NBA Parlay Builder:")
    parlay_url = f"{base_url}/api/sports/30/parlays/builder?leg_count=2&max_results=3"
    
    try:
        response = requests.get(parlay_url, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            parlays = data.get('parlays', [])
            print(f"   Found {len(parlays)} NBA parlays")
            
            if parlays:
                for parlay in parlays[:2]:
                    print(f"   - Parlay EV: {parlay.get('total_ev', 0):.2%}")
                    print(f"     Legs: {len(parlay.get('legs', []))}")
            else:
                print("   No NBA parlays yet")
        else:
            print(f"   Error: {response.text[:100]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    test_nba_stub()
