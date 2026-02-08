#!/usr/bin/env python3
"""
Check Super Bowl game details
"""
import requests

def check_super_bowl():
    """Check Super Bowl game details"""
    base_url = "https://railway-engine-production.up.railway.app"
    
    print("CHECKING SUPER BOWL DETAILS")
    print("="*80)
    
    # Get NFL games
    print("\n1. NFL Games Today:")
    nfl_url = f"{base_url}/api/sports/31/games/today"
    
    try:
        response = requests.get(nfl_url, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            games = data.get('items', [])
            print(f"   Found {len(games)} NFL games")
            
            for game in games:
                print(f"\n   {game.get('away_team', 'N/A')} @ {game.get('home_team', 'N/A')}")
                print(f"   Time: {game.get('start_time', 'N/A')}")
                print(f"   Game ID: {game.get('id', 'N/A')}")
                
                # Convert UTC time to CT
                if 'start_time' in game:
                    try:
                        from datetime import datetime, timezone, timedelta
                        utc_time = datetime.fromisoformat(game['start_time'].replace('Z', '+00:00'))
                        ct_time = utc_time - timedelta(hours=6)  # UTC to CT
                        print(f"   CT Time: {ct_time.strftime('%I:%M %p CT')}")
                    except:
                        pass
    except Exception as e:
        print(f"   Error: {e}")
    
    # Check NFL odds
    print("\n2. NFL Odds:")
    nfl_odds_url = f"{base_url}/api/nfl/odds"
    
    try:
        response = requests.get(nfl_odds_url, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   NFL odds data: {data}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Check best odds for NFL
    print("\n3. Best NFL Odds:")
    best_odds_url = f"{base_url}/api/odds/best?limit=20"
    
    try:
        response = requests.get(best_odds_url, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            odds_list = data if isinstance(data, list) else []
            
            # Filter for NFL games (assuming game_id 704+ might be NFL)
            nfl_odds = [odd for odd in odds_list if odd.get('game_id', 0) >= 704]
            
            print(f"   Found {len(nfl_odds)} NFL odds entries")
            
            for odd in nfl_odds[:5]:
                game_id = odd.get('game_id')
                market = odd.get('market_type', 'N/A')
                side = odd.get('side', 'N/A')
                best_odds = odd.get('best_odds', 'N/A')
                best_book = odd.get('best_sportsbook', 'N/A')
                print(f"   Game {game_id} - {market} {side}: {best_odds} ({best_book})")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n" + "="*80)
    print("SUPER BOWL INFO:")
    print("- Teams: Seahawks vs Patriots")
    print("- Time: 5:30 PM CT")
    print("- Network: NBC/Peacock")
    print("- Records: Both 14-3")
    print("="*80)

if __name__ == "__main__":
    check_super_bowl()
