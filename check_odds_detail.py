#!/usr/bin/env python3
"""
Check odds data in detail
"""
import requests

def check_odds_detail():
    """Check odds data in detail"""
    base_url = "https://railway-engine-production.up.railway.app"
    
    print("CHECKING ODDS DATA IN DETAIL")
    print("="*80)
    
    # Get best odds
    print("\n1. Best Odds Details:")
    best_odds_url = f"{base_url}/api/odds/best?limit=20"
    
    try:
        response = requests.get(best_odds_url, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            odds_list = data if isinstance(data, list) else []
            print(f"   Found {len(odds_list)} odds entries")
            
            # Group by game
            games = {}
            for odd in odds_list:
                game_id = odd.get('game_id')
                if game_id not in games:
                    games[game_id] = []
                games[game_id].append(odd)
            
            print(f"   Odds for {len(games)} games:")
            
            for game_id, game_odds in list(games.items())[:3]:
                print(f"\n   Game ID {game_id}:")
                
                # Get game info
                game_url = f"{base_url}/api/sports/30/games/{game_id}"
                try:
                    game_response = requests.get(game_url, timeout=5)
                    if game_response.status_code == 200:
                        game_data = game_response.json()
                        print(f"     {game_data.get('away_team', 'N/A')} @ {game_data.get('home_team', 'N/A')}")
                except:
                    pass
                
                # Show odds
                for odd in game_odds[:5]:
                    market = odd.get('market_type', 'N/A')
                    side = odd.get('side', 'N/A')
                    best_odds = odd.get('best_odds', 'N/A')
                    best_book = odd.get('best_sportsbook', 'N/A')
                    lines = odd.get('lines', [])
                    
                    print(f"     {market} {side}: {best_odds} ({best_book})")
                    
                    # Show all sportsbooks
                    for line in lines[:3]:
                        book = line.get('sportsbook', 'N/A')
                        odds = line.get('odds', 'N/A')
                        print(f"       - {book}: {odds}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Check NBA odds specifically
    print("\n2. NBA Odds:")
    nba_odds_url = f"{base_url}/api/data/v2/odds/nba"
    
    try:
        response = requests.get(nba_odds_url, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   NBA odds data: {data}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    check_odds_detail()
