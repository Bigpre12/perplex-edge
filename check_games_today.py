#!/usr/bin/env python3
"""
Check NBA games and Super Bowl data
"""
import requests
import json

def check_games():
    """Check NBA games and Super Bowl"""
    base_url = "https://railway-engine-production.up.railway.app"
    
    print("CHECKING NBA GAMES AND SUPER BOWL")
    print("="*80)
    
    # Check NBA games (sport_id=30)
    print("\n1. NBA Games (sport_id=30):")
    nba_url = f"{base_url}/api/sports/30/games/today"
    
    try:
        response = requests.get(nba_url, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            games = data.get('items', [])
            print(f"   Found {len(games)} NBA games")
            
            for game in games[:3]:
                print(f"   - {game.get('home_team', 'N/A')} vs {game.get('away_team', 'N/A')}")
                print(f"     Time: {game.get('start_time', 'N/A')}")
        else:
            print(f"   Error: {response.text[:100]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Check NFL games (sport_id=31) - Super Bowl
    print("\n2. NFL Games (sport_id=31) - Super Bowl:")
    nfl_url = f"{base_url}/api/sports/31/games/today"
    
    try:
        response = requests.get(nfl_url, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            games = data.get('items', [])
            print(f"   Found {len(games)} NFL games")
            
            for game in games[:3]:
                print(f"   - {game.get('home_team', 'N/A')} vs {game.get('away_team', 'N/A')}")
                print(f"     Time: {game.get('start_time', 'N/A')}")
        else:
            print(f"   Error: {response.text[:100]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Check available sports
    print("\n3. Available Sports:")
    sports_url = f"{base_url}/api/sports"
    
    try:
        response = requests.get(sports_url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            for sport in data.get('items', []):
                if sport.get('id') in [30, 31]:  # NBA and NFL
                    print(f"   - {sport.get('name')} (ID: {sport.get('id')})")
    except:
        pass
    
    print("\n" + "="*80)

if __name__ == "__main__":
    check_games()
