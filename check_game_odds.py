#!/usr/bin/env python3
"""
Check game data with odds and matchups
"""
import requests

def check_game_odds():
    """Check game data with odds"""
    base_url = "https://railway-engine-production.up.railway.app"
    
    print("CHECKING GAME DATA WITH ODDS")
    print("="*80)
    
    # Check NBA games with more details
    print("\n1. NBA Games with Details:")
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
                
                # Check for odds
                if 'lines' in game:
                    lines = game['lines']
                    if lines:
                        print(f"   Available Lines:")
                        for line in lines[:3]:
                            print(f"     - {line.get('bet_type', 'N/A')}: {line.get('line_value', 'N/A')} ({line.get('side', 'N/A')})")
                else:
                    print("   No odds data available")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Check odds endpoint
    print("\n2. Odds Endpoint:")
    odds_url = f"{base_url}/api/odds/lines/compare?game_id=1"
    
    try:
        response = requests.get(odds_url, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Odds data available: {len(data) if isinstance(data, list) else 'dict'}")
        else:
            print(f"   Error: {response.text[:100]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Check if we have draftkings data
    print("\n3. Check for DraftKings Data:")
    dk_url = f"{base_url}/api/odds/draftkings"
    
    try:
        response = requests.get(dk_url, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   DraftKings data: {data}")
        else:
            print(f"   Error: {response.text[:100]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    check_game_odds()
