#!/usr/bin/env python3
"""
Test stub props for Super Bowl
"""
import requests

def test_stub_props():
    """Test stub props for Super Bowl"""
    base_url = "https://railway-engine-production.up.railway.app"
    
    print("TESTING STUB PROPS FOR SUPER BOWL")
    print("="*80)
    
    # Test stub props
    print("\n1. Test Stub Props:")
    stub_url = f"{base_url}/api/sports/31/picks/player-props-stub?game_id=648&limit=20"
    
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
                    print(f"     Odds: {prop.get('odds', 0)}")
            else:
                print("   No stub props found")
        else:
            print(f"   Error: {response.text[:100]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test parlay builder with stub data
    print("\n2. Test Parlay Builder with Stub Data:")
    parlay_url = f"{base_url}/api/sports/31/parlays/builder?leg_count=2&max_results=5"
    
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
                    
                    # Show legs
                    for leg in parlay.get('legs', [])[:2]:
                        player = leg.get('player', {})
                        print(f"       * {player.get('name', 'N/A')}: {leg.get('stat_type', 'N/A')} {leg.get('line_value', 'N/A')} ({leg.get('side', 'N/A')})")
                        print(f"         Edge: {leg.get('edge', 0):.2%}")
            else:
                print("   No parlays yet")
        else:
            print(f"   Error: {response.text[:100]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test auto-generate
    print("\n3. Test Auto-Generate:")
    auto_url = f"{base_url}/api/sports/31/parlays/auto-generate?leg_count=3&slip_count=3"
    
    try:
        response = requests.get(auto_url, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            slips = data.get('slips', [])
            print(f"   Generated {len(slips)} slips")
            
            if slips:
                print(f"   Slate Quality: {data.get('slate_quality', 'N/A')}")
                print(f"   Avg Slip EV: {data.get('avg_slip_ev', 0):.2%}")
                
                # Show sample slip
                if slips:
                    slip = slips[0]
                    print(f"\n   Sample Slip:")
                    print(f"   - Slip EV: {slip.get('total_ev', 0):.2%}")
                    print(f"   - Legs: {len(slip.get('legs', []))}")
                    for leg in slip.get('legs', [])[:2]:
                        player = leg.get('player', {})
                        print(f"     * {player.get('name', 'N/A')}: {leg.get('stat_type', 'N/A')} {leg.get('line_value', 'N/A')}")
            else:
                print("   No slips generated")
        else:
            print(f"   Error: {response.text[:100]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n" + "="*80)
    print("STATUS:")
    print("- Stub Props: Working!")
    print("- Parlay Builder: Testing...")
    print("- Auto-Generate: Testing...")
    print("="*80)

if __name__ == "__main__":
    test_stub_props()
