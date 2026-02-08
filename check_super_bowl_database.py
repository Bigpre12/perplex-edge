#!/usr/bin/env python3
"""
Check Super Bowl game and props in database
"""
import requests
import json

def check_super_bowl_database():
    """Check Super Bowl game and props"""
    base_url = "https://railway-engine-production.up.railway.app"
    
    print("CHECKING SUPER BOWL DATABASE")
    print("="*80)
    
    # First, let's check if we can query the database directly
    print("\n1. Check NFL Super Bowl Game:")
    games_url = f"{base_url}/api/sports/31/games/today"
    
    try:
        response = requests.get(games_url, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            games = data.get('items', [])
            print(f"   Found {len(games)} NFL games today")
            
            for game in games:
                print(f"\n   Game ID: {game.get('id')}")
                print(f"   {game.get('away_team', 'N/A')} @ {game.get('home_team', 'N/A')}")
                print(f"   Time: {game.get('start_time', 'N/A')}")
                
                # Check if this is the Super Bowl (Seahawks vs Patriots)
                away = game.get('away_team', '').lower()
                home = game.get('home_team', '').lower()
                if 'seahawks' in away and 'patriots' in home:
                    print("   ✓ THIS IS THE SUPER BOWL!")
                    super_bowl_game_id = game.get('id')
                    
                    # Now check for props for this game
                    print(f"\n2. Checking props for Game ID {super_bowl_game_id}:")
                    
                    # Check player props
                    props_url = f"{base_url}/api/sports/31/picks/player-props?game_id={super_bowl_game_id}&limit=50"
                    try:
                        props_response = requests.get(props_url, timeout=10)
                        print(f"      Status: {props_response.status_code}")
                        
                        if props_response.status_code == 200:
                            props_data = props_response.json()
                            props = props_data.get('items', [])
                            print(f"      Found {len(props)} player props")
                            
                            # Look for QB props
                            qb_props = []
                            for prop in props:
                                player_name = prop.get('player', {}).get('name', '')
                                if any(qb in player_name.lower() for qb in ['maye', 'darnold']):
                                    qb_props.append(prop)
                            
                            print(f"      QB props: {len(qb_props)}")
                            for prop in qb_props[:5]:
                                player = prop.get('player', {})
                                print(f"        - {player.get('name', 'N/A')}: {prop.get('stat_type', 'N/A')} {prop.get('line_value', 'N/A')} ({prop.get('side', 'N/A')})")
                                print(f"          Edge: {prop.get('edge', 0):.2%}")
                        else:
                            print(f"      Error: {props_response.text[:100]}")
                    except Exception as e:
                        print(f"      Error: {e}")
                    
                    # Check all picks for this game
                    all_picks_url = f"{base_url}/api/sports/31/picks?game_id={super_bowl_game_id}&limit=50"
                    try:
                        all_response = requests.get(all_picks_url, timeout=10)
                        print(f"\n3. All picks for Game ID {super_bowl_game_id}:")
                        print(f"      Status: {all_response.status_code}")
                        
                        if all_response.status_code == 200:
                            all_data = all_response.json()
                            all_picks = all_data.get('items', [])
                            print(f"      Total picks: {len(all_picks)}")
                            
                            # Group by player
                            player_picks = {}
                            for pick in all_picks:
                                player_name = pick.get('player', {}).get('name', 'Unknown')
                                if player_name not in player_picks:
                                    player_picks[player_name] = []
                                player_picks[player_name].append(pick)
                            
                            print(f"      Players with props: {len(player_picks)}")
                            for player, picks in list(player_picks.items())[:10]:
                                print(f"        - {player}: {len(picks)} props")
                        else:
                            print(f"      Error: {all_response.text[:100]}")
                    except Exception as e:
                        print(f"      Error: {e}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n" + "="*80)
    print("QUARTERBACK MATCHUP:")
    print("- Patriots: Drake Maye (rookie sensation)")
    print("- Seahawks: Sam Darnold (redemption story)")
    print("="*80)

if __name__ == "__main__":
    check_super_bowl_database()
