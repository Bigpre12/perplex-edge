#!/usr/bin/env python3
"""
Create stub props for Super Bowl
"""
import requests

def create_stub_props():
    """Create stub props for Super Bowl"""
    base_url = "https://railway-engine-production.up.railway.app"
    
    print("CREATING STUB PROPS FOR SUPER BOWL")
    print("="*80)
    
    # Create a simple stub endpoint
    print("\n1. Create Stub Props Endpoint:")
    stub_url = f"{base_url}/api/sports/31/picks/player-props-stub"
    
    try:
        response = requests.get(stub_url, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            props = data.get('items', [])
            print(f"   Found {len(props)} stub props")
            
            if props:
                # Look for QB props
                qb_props = []
                for prop in props:
                    player_name = prop.get('player', {}).get('name', '').lower()
                    if 'maye' in player_name or 'darnold' in player_name:
                        qb_props.append(prop)
                
                print(f"\n   QB Props ({len(qb_props)}):")
                for prop in qb_props:
                    player = prop.get('player', {})
                    print(f"   - {player.get('name', 'N/A')}: {prop.get('stat_type', 'N/A')} {prop.get('line_value', 'N/A')} ({prop.get('side', 'N/A')})")
                    print(f"     Edge: {prop.get('edge', 0):.2%}")
                    print(f"     Confidence: {prop.get('confidence_score', 0):.2%}")
            else:
                print("   No stub props found")
        else:
            print(f"   Error: {response.text[:100]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test parlay builder with stub data
    print("\n2. Test Parlay Builder with Stub Data:")
    parlay_url = f"{base_url}/api/sports/31/parlays/builder-stub?leg_count=2&max_results=3"
    
    try:
        response = requests.get(parlay_url, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            parlays = data.get('parlays', [])
            print(f"   Found {len(parlays)} parlays")
            
            if parlays:
                for parlay in parlays[:3]:
                    print(f"   - Parlay EV: {parlay.get('total_ev', 0):.2%}")
                    print(f"     Legs: {len(parlay.get('legs', []))}")
                    print(f"     Model Status: {parlay.get('model_status', {}).get('status', 'N/A')}")
            else:
                print("   No parlays yet")
        else:
            print(f"   Error: {response.text[:100]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    create_stub_props()
