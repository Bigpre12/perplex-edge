#!/usr/bin/env python3
"""
Test parlay builder with NBA and NFL
"""
import requests

def test_parlay_with_games():
    """Test parlay builder with NBA and NFL"""
    base_url = "https://railway-engine-production.up.railway.app"
    
    print("TESTING PARLAY BUILDER WITH NBA AND NFL")
    print("="*80)
    
    # Test NBA parlay builder
    print("\n1. NBA Parlay Builder (sport_id=30):")
    nba_url = f"{base_url}/api/sports/30/parlays/builder?leg_count=3&max_results=3"
    
    try:
        response = requests.get(nba_url, timeout=15)
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
                print("   No NBA parlays available")
        else:
            print(f"   Error: {response.text[:100]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test NFL parlay builder
    print("\n2. NFL Parlay Builder (sport_id=31):")
    nfl_url = f"{base_url}/api/sports/31/parlays/builder?leg_count=3&max_results=3"
    
    try:
        response = requests.get(nfl_url, timeout=15)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            parlays = data.get('parlays', [])
            print(f"   Found {len(parlays)} NFL parlays")
            
            if parlays:
                for parlay in parlays[:2]:
                    print(f"   - Parlay EV: {parlay.get('total_ev', 0):.2%}")
                    print(f"     Legs: {len(parlay.get('legs', []))}")
            else:
                print("   No NFL parlays available")
        else:
            print(f"   Error: {response.text[:100]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test auto-generate for NBA
    print("\n3. NBA Auto-Generate (sport_id=30):")
    nba_auto_url = f"{base_url}/api/sports/30/parlays/auto-generate?leg_count=4&slip_count=2"
    
    try:
        response = requests.get(nba_auto_url, timeout=15)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            slips = data.get('slips', [])
            print(f"   Generated {len(slips)} NBA slips")
            
            if slips:
                print(f"   Slate quality: {data.get('slate_quality', 'N/A')}")
                print(f"   Avg slip EV: {data.get('avg_slip_ev', 0):.2%}")
            else:
                print("   No NBA slips generated")
        else:
            print(f"   Error: {response.text[:100]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    test_parlay_with_games()
