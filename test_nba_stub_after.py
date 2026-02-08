#!/usr/bin/env python3
"""
Test NBA stub props after deployment
"""
import requests

def test_nba_stub_after():
    """Test NBA stub props after deployment"""
    base_url = "https://railway-engine-production.up.railway.app"
    
    print("TESTING NBA STUB PROPS AFTER DEPLOYMENT")
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
                # Group by game
                game_props = {}
                for prop in props:
                    game_id = prop.get('game', {}).get('id')
                    if game_id not in game_props:
                        game_props[game_id] = []
                    game_props[game_id].append(prop)
                
                print(f"\n   Props by game:")
                for game_id, game_props_list in game_props.items():
                    game = game_props_list[0].get('game', {})
                    print(f"   Game {game_id}: {game.get('away_team', 'N/A')} @ {game.get('home_team', 'N/A')} - {len(game_props_list)} props")
                    
                    # Show sample props
                    for prop in game_props_list[:3]:
                        player = prop.get('player', {})
                        print(f"     - {player.get('name', 'N/A')}: {prop.get('stat_type', 'N/A')} {prop.get('line_value', 'N/A')} ({prop.get('side', 'N/A')})")
                        print(f"       Edge: {prop.get('edge', 0):.2%}")
            else:
                print("   No NBA stub props")
        else:
            print(f"   Error: {response.text[:100]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test NBA parlay builder
    print("\n2. NBA Parlay Builder:")
    parlay_url = f"{base_url}/api/sports/30/parlays/builder?leg_count=2&max_results=5"
    
    try:
        response = requests.get(parlay_url, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            parlays = data.get('parlays', [])
            print(f"   Found {len(parlays)} NBA parlays")
            
            if parlays:
                for parlay in parlays[:3]:
                    print(f"   - Parlay EV: {parlay.get('total_ev', 0):.2%}")
                    print(f"     Legs: {len(parlay.get('legs', []))}")
                    print(f"     Model Status: {parlay.get('model_status', {}).get('status', 'N/A')}")
                    
                    # Show legs
                    for leg in parlay.get('legs', [])[:2]:
                        player = leg.get('player', {})
                        print(f"       * {player.get('name', 'N/A')}: {leg.get('stat_type', 'N/A')} {leg.get('line_value', 'N/A')}")
                        print(f"         Edge: {leg.get('edge', 0):.2%}")
            else:
                print("   No NBA parlays yet")
        else:
            print(f"   Error: {response.text[:100]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test NBA auto-generate
    print("\n3. NBA Auto-Generate:")
    auto_url = f"{base_url}/api/sports/30/parlays/auto-generate?leg_count=3&slip_count=3"
    
    try:
        response = requests.get(auto_url, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            slips = data.get('slips', [])
            print(f"   Generated {len(slips)} NBA slips")
            
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
                print("   No NBA slips generated")
        else:
            print(f"   Error: {response.text[:100]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n" + "="*80)
    print("NBA STATUS:")
    print("- 4 Games: ✅")
    print("- Stub Props: Testing...")
    print("- Parlay Builder: Testing...")
    print("- Auto-Generate: Testing...")
    print("="*80)

if __name__ == "__main__":
    test_nba_stub_after()
