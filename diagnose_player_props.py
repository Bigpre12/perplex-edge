#!/usr/bin/env python3
"""
Diagnose and fix player props not loading
"""
import requests
import time

def diagnose_player_props():
    """Diagnose and fix player props not loading"""
    base_url = "https://railway-engine-production.up.railway.app"
    
    print("DIAGNOSING PLAYER PROPS NOT LOADING")
    print("="*80)
    
    print("\n1. Current Time Status:")
    from datetime import datetime
    now = datetime.now()
    super_bowl = datetime(2026, 2, 8, 17, 30)  # 5:30 PM CT
    time_left = super_bowl - now
    hours_left = time_left.total_seconds() / 3600
    
    print(f"   Current time: {now.strftime('%I:%M %p')}")
    print(f"   Super Bowl kickoff: 5:30 PM CT")
    print(f"   Time left: {hours_left:.1f} hours")
    
    if hours_left < 1:
        print("   Status: URGENT - Less than 1 hour!")
    elif hours_left < 2:
        print("   Status: CRITICAL - Less than 2 hours!")
    else:
        print("   Status: Time running out")
    
    print("\n2. Testing Backend Health:")
    try:
        response = requests.get(f"{base_url}/api/health", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Backend is healthy: {data.get('status', 'unknown')}")
        else:
            print(f"   Backend unhealthy: {response.text[:100]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n3. Testing NBA Player Props:")
    try:
        response = requests.get(f"{base_url}/api/sports/30/picks/player-props?limit=5", timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            props = data.get('items', [])
            print(f"   SUCCESS: Found {len(props)} NBA props")
            
            if props:
                for i, prop in enumerate(props[:3], 1):
                    player = prop.get('player', {})
                    print(f"   {i}. {player.get('name', 'N/A')}: {prop.get('stat_type', 'N/A')} {prop.get('line_value', 'N/A')}")
            else:
                print("   No props found - might be empty")
        elif response.status_code == 500:
            error_text = response.text
            print(f"   500 Error: {error_text[:100]}")
            
            # Check for specific errors
            if "closing_odds" in error_text:
                print("   Issue: CLV columns still missing")
            elif "column" in error_text and "does not exist" in error_text:
                print("   Issue: Database column missing")
            else:
                print("   Issue: Unknown database error")
        else:
            print(f"   Error: {response.text[:100]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n4. Testing NFL Super Bowl Props:")
    try:
        response = requests.get(f"{base_url}/api/sports/31/picks/player-props?game_id=648&limit=5", timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            props = data.get('items', [])
            print(f"   SUCCESS: Found {len(props)} NFL props")
            
            if props:
                for i, prop in enumerate(props[:3], 1):
                    player = prop.get('player', {})
                    print(f"   {i}. {player.get('name', 'N/A')}: {prop.get('stat_type', 'N/A')} {prop.get('line_value', 'N/A')}")
        else:
            print(f"   Error: {response.text[:100]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n5. Testing Games Data:")
    try:
        response = requests.get(f"{base_url}/api/sports/30/games?limit=5", timeout=10)
        print(f"   NBA Games Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            games = data.get('items', [])
            print(f"   Found {len(games)} NBA games")
            
            if games:
                game = games[0]
                print(f"   Sample: {game.get('home_team', {}).get('name', 'N/A')} vs {game.get('away_team', {}).get('name', 'N/A')}")
        else:
            print(f"   Error: {response.text[:100]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    try:
        response = requests.get(f"{base_url}/api/sports/31/games?limit=5", timeout=10)
        print(f"   NFL Games Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            games = data.get('items', [])
            print(f"   Found {len(games)} NFL games")
            
            if games:
                game = games[0]
                print(f"   Sample: {game.get('home_team', {}).get('name', 'N/A')} vs {game.get('away_team', {}).get('name', 'N/A')}")
        else:
            print(f"   Error: {response.text[:100]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n6. Testing Players Data:")
    try:
        response = requests.get(f"{base_url}/api/sports/30/players?limit=5", timeout=10)
        print(f"   NBA Players Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            players = data.get('items', [])
            print(f"   Found {len(players)} NBA players")
            
            if players:
                player = players[0]
                print(f"   Sample: {player.get('name', 'N/A')} - {player.get('position', 'N/A')}")
        else:
            print(f"   Error: {response.text[:100]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n" + "="*80)
    print("DIAGNOSIS RESULTS:")
    print("="*80)
    
    print("\nCOMMON ISSUES:")
    print("1. CLV columns missing from database")
    print("2. Database connection issues")
    print("3. No player props data available")
    print("4. API endpoint errors")
    print("5. Frontend-backend connection issues")
    
    print("\n" + "="*80)
    print("IMMEDIATE FIXES NEEDED:")
    print("="*80)
    
    print("\n1. If 500 errors with CLV columns:")
    print("   - Add CLV columns to database")
    print("   - Or comment out CLV references in code")
    
    print("\n2. If no props found:")
    print("   - Sync data from The Odds API")
    print("   - Check if games are scheduled")
    print("   - Generate picks for games")
    
    print("\n3. If frontend 502 errors:")
    print("   - Set BACKEND_URL in Railway frontend")
    print("   - Value: https://railway-engine-production.up.railway.app")
    
    print("\n" + "="*80)
    print("URGENCY: SUPER BOWL COUNTDOWN")
    print("="*80)
    
    if hours_left < 2:
        print("CRITICAL: Less than 2 hours to Super Bowl!")
        print("Need immediate fixes to get player props working!")
        print("Priority: Get basic props loading, then optimize")
    else:
        print("Time is running out - need fast fixes!")
    
    print("\n" + "="*80)
    print("NEXT STEPS:")
    print("1. Identify specific error from test results")
    print("2. Apply targeted fix")
    print("3. Test immediately")
    print("4. If working, deploy to production")
    print("5. Test Super Bowl props specifically")
    print("="*80)

if __name__ == "__main__":
    diagnose_player_props()
