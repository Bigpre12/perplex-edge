#!/usr/bin/env python3
"""
Check NBA games and picks for today
"""
import requests

def check_nba_games_picks():
    """Check NBA games and picks for today"""
    base_url = "https://railway-engine-production.up.railway.app"
    
    print("CHECKING NBA GAMES AND PICKS FOR TODAY")
    print("="*80)
    
    # Get NBA games
    print("\n1. NBA Games Today:")
    games_url = f"{base_url}/api/sports/30/games/today"
    
    try:
        response = requests.get(games_url, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            games = data.get('items', [])
            print(f"   Found {len(games)} NBA games")
            
            for game in games:
                print(f"\n   {game.get('away_team', 'N/A')} @ {game.get('home_team', 'N/A')}")
                print(f"   Time: {game.get('start_time', 'N/A')}")
                print(f"   Game ID: {game.get('id', 'N/A')}")
                
                # Check picks for this game
                game_id = game.get('id')
                picks_url = f"{base_url}/api/sports/30/picks/player-props?game_id={game_id}&limit=100"
                
                try:
                    picks_response = requests.get(picks_url, timeout=5)
                    if picks_response.status_code == 200:
                        picks_data = picks_response.json()
                        picks = picks_data.get('items', [])
                        
                        active_picks = [p for p in picks if p.get('is_active', True)]
                        avg_ev = sum(p.get('edge', 0) for p in picks) / len(picks) if picks else 0
                        
                        print(f"   Picks: {len(picks)} total, {len(active_picks)} active")
                        print(f"   Avg EV: {avg_ev:.2%}")
                        
                        # Show sample picks
                        if picks:
                            print(f"   Sample props:")
                            for pick in picks[:5]:
                                player = pick.get('player', {})
                                print(f"     - {player.get('name', 'N/A')}: {pick.get('stat_type', 'N/A')} {pick.get('line_value', 'N/A')} ({pick.get('side', 'N/A')})")
                                print(f"       Edge: {pick.get('edge', 0):.2%}")
                    else:
                        print(f"   Picks: Error fetching picks")
                except:
                    print(f"   Picks: Timeout or error")
        else:
            print(f"   Error: {response.text[:100]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Check total NBA picks
    print("\n2. Total NBA Picks Summary:")
    all_picks_url = f"{base_url}/api/sports/30/picks/player-props?limit=200"
    
    try:
        response = requests.get(all_picks_url, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            all_picks = data.get('items', [])
            
            active_picks = [p for p in all_picks if p.get('is_active', True)]
            avg_ev = sum(p.get('edge', 0) for p in all_picks) / len(all_picks) if all_picks else 0
            
            print(f"   Total NBA Picks: {len(all_picks)}")
            print(f"   Active Picks: {len(active_picks)}")
            print(f"   Average EV: {avg_ev:.2%}")
            
            # Group by game
            game_picks = {}
            for pick in all_picks:
                game_id = pick.get('game_id')
                if game_id not in game_picks:
                    game_picks[game_id] = []
                game_picks[game_id].append(pick)
            
            print(f"\n   Picks per game:")
            for game_id, picks in game_picks.items():
                active = [p for p in picks if p.get('is_active', True)]
                print(f"   Game {game_id}: {len(picks)} total, {len(active)} active")
        else:
            print(f"   Error: {response.text[:100]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Check if we can activate picks
    print("\n3. Check Activation Endpoint:")
    activate_url = f"{base_url}/api/grading/admin/activate-test-picks?count=160&sport_id=30"
    
    try:
        response = requests.post(activate_url, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Activation result: {data}")
        else:
            print(f"   Error: {response.text[:100]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n" + "="*80)
    print("NBA STATUS:")
    print("- Games: Checking...")
    print("- Picks: Checking...")
    print("- Activation: Testing...")
    print("="*80)

if __name__ == "__main__":
    check_nba_games_picks()
