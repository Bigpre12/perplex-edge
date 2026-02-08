#!/usr/bin/env python3
"""
Debug why no parlays are being generated
"""
import requests

def debug_parlay_generation():
    """Debug parlay generation"""
    base_url = "https://railway-engine-production.up.railway.app"
    
    print("DEBUGGING PARLAY GENERATION")
    print("="*80)
    
    # Check if there are any picks at all for NBA
    print("\n1. Check all NBA picks (not just player props):")
    all_picks_url = f"{base_url}/api/sports/30/picks?limit=10"
    
    try:
        response = requests.get(all_picks_url, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            picks = data.get('items', [])
            print(f"   Found {len(picks)} total NBA picks")
            
            if picks:
                for pick in picks[:3]:
                    print(f"   - {pick.get('player', {}).get('name', 'N/A')}: {pick.get('stat_type', 'N/A')}")
                    print(f"     Edge: {pick.get('edge', 0):.2%}")
        else:
            print(f"   Error: {response.text[:100]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Check game lines for NBA
    print("\n2. Check NBA game lines:")
    game_lines_url = f"{base_url}/api/sports/30/picks/game-lines?limit=10"
    
    try:
        response = requests.get(game_lines_url, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            picks = data.get('items', [])
            print(f"   Found {len(picks)} NBA game line picks")
            
            if picks:
                for pick in picks[:3]:
                    print(f"   - {pick.get('game', {}).get('home_team', 'N/A')} vs {pick.get('game', {}).get('away_team', 'N/A')}")
                    print(f"     {pick.get('bet_type', 'N/A')} {pick.get('line_value', 'N/A')}")
        else:
            print(f"   Error: {response.text[:100]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Check markets available
    print("\n3. Check available markets for NBA:")
    markets_url = f"{base_url}/api/sports/30/markets"
    
    try:
        response = requests.get(markets_url, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            markets = data.get('items', [])
            print(f"   Found {len(markets)} markets")
            
            for market in markets[:5]:
                print(f"   - {market.get('stat_type', 'N/A')}: {market.get('count', 0)} picks")
        else:
            print(f"   Error: {response.text[:100]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    debug_parlay_generation()
