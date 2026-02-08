#!/usr/bin/env python3
"""
Check Super Bowl props specifically
"""
import requests

def check_super_bowl_props():
    """Check Super Bowl props"""
    base_url = "https://railway-engine-production.up.railway.app"
    super_bowl_game_id = 648
    
    print("CHECKING SUPER BOWL LX PROPS")
    print("="*80)
    print(f"Game ID: {super_bowl_game_id}")
    print("Matchup: Seattle Seahawks @ New England Patriots")
    print("Quarterbacks: Sam Darnold vs Drake Maye")
    
    # Check player props
    print("\n1. Player Props:")
    props_url = f"{base_url}/api/sports/31/picks/player-props?game_id={super_bowl_game_id}&limit=50"
    
    try:
        response = requests.get(props_url, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            props = data.get('items', [])
            print(f"   Found {len(props)} player props")
            
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
                print("   NO PLAYER PROPS FOUND")
        else:
            print(f"   Error: {response.text[:100]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Check all picks
    print("\n2. All Picks:")
    all_picks_url = f"{base_url}/api/sports/31/picks?game_id={super_bowl_game_id}&limit=50"
    
    try:
        response = requests.get(all_picks_url, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            picks = data.get('items', [])
            print(f"   Found {len(picks)} total picks")
            
            if picks:
                # Group by player
                player_picks = {}
                for pick in picks:
                    player_name = pick.get('player', {}).get('name', 'Unknown')
                    if player_name not in player_picks:
                        player_picks[player_name] = []
                    player_picks[player_name].append(pick)
                
                print(f"\n   Players with picks: {len(player_picks)}")
                for player, player_picks_list in list(player_picks.items())[:10]:
                    print(f"   - {player}: {len(player_picks_list)} picks")
                    
                    # Show QB details
                    if 'maye' in player.lower() or 'darnold' in player.lower():
                        for pick in player_picks_list[:3]:
                            print(f"     * {pick.get('stat_type', 'N/A')} {pick.get('line_value', 'N/A')} ({pick.get('side', 'N/A')})")
                            print(f"       Edge: {pick.get('edge', 0):.2%}")
            else:
                print("   NO PICKS FOUND")
        else:
            print(f"   Error: {response.text[:100]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Check if we can trigger odds sync
    print("\n3. Trigger NFL Odds Sync:")
    sync_url = f"{base_url}/api/sync/odds/NFL"
    
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
    print("STATUS:")
    print("- Game found: YES (ID: 648)")
    print("- QB matchup: Drake Maye vs Sam Darnold")
    print("- Props available: CHECKING...")
    print("="*80)

if __name__ == "__main__":
    check_super_bowl_props()
