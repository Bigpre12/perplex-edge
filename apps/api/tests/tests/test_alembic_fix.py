#!/usr/bin/env python3
"""
Test if Alembic fix worked and deployment is working
"""
import requests
import time

def test_alembic_fix():
    """Test if Alembic fix worked and deployment is working"""
    base_url = "https://railway-engine-production.up.railway.app"
    
    print("TESTING ALEMBIC FIX AND DEPLOYMENT")
    print("="*80)
    
    print("\n1. Alembic fix deployed!")
    print("   Commit: 9daea51")
    print("   Fixed: Tuple unpacking error in migration")
    
    print("\n2. Waiting for deployment...")
    time.sleep(30)
    
    print("\n3. Testing backend health:")
    try:
        response = requests.get(f"{base_url}/api/health", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   SUCCESS: Backend is healthy!")
        else:
            print(f"   Error: {response.text[:100]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n4. Testing clean player props:")
    try:
        response = requests.get(f"{base_url}/clean/clean-player-props?sport_id=31&limit=5", timeout=10)
        print(f"   Clean NFL Props Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            props = data.get('items', [])
            print(f"   SUCCESS! Found {len(props)} NFL props")
            
            if props:
                for i, prop in enumerate(props[:3], 1):
                    player = prop.get('player', {})
                    market = prop.get('market', {})
                    print(f"   {i}. {player.get('name', 'N/A')}: {market.get('stat_type', 'N/A')} {prop.get('line_value', 'N/A')}")
                    print(f"      Edge: {prop.get('edge', 0):.2%}")
                    print(f"      Odds: {prop.get('odds', 0)}")
        else:
            print(f"   Error: {response.text[:100]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n5. Testing Super Bowl props:")
    try:
        response = requests.get(f"{base_url}/clean/super-bowl-props", timeout=10)
        print(f"   Super Bowl Props Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            props = data.get('items', [])
            print(f"   SUCCESS! Found {len(props)} Super Bowl props")
            
            if props:
                print(f"   Super Bowl props:")
                for i, prop in enumerate(props[:5], 1):
                    player = prop.get('player', {})
                    market = prop.get('market', {})
                    print(f"   {i}. {player.get('name', 'N/A')}: {market.get('stat_type', 'N/A')} {prop.get('line_value', 'N/A')}")
                    print(f"      Edge: {prop.get('edge', 0):.2%}")
                    print(f"      Confidence: {prop.get('confidence_score', 0):.1f}")
        else:
            print(f"   Error: {response.text[:100]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n6. Testing original picks endpoint:")
    try:
        response = requests.get(f"{base_url}/api/sports/31/picks/player-props?game_id=648&limit=5", timeout=10)
        print(f"   Original NFL Picks Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            props = data.get('items', [])
            print(f"   SUCCESS! Found {len(props)} NFL props")
        elif response.status_code == 500:
            print(f"   Still 500 error - CLV columns still missing")
        else:
            print(f"   Error: {response.text[:100]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n" + "="*80)
    print("ALEMBIC FIX RESULTS:")
    print("="*80)
    
    print("\nIF DEPLOYMENT WORKS:")
    print("1. Backend should be healthy (200)")
    print("2. Clean endpoints should work (200)")
    print("3. Original picks might still fail (500)")
    print("4. Use clean endpoints for Super Bowl!")
    
    print("\nIF STILL FAILING:")
    print("1. Wait 2 more minutes for deployment")
    print("2. Use emergency mock data")
    print("3. Time is critical!")
    
    print("\nTIME STATUS:")
    from datetime import datetime
    now = datetime.now()
    super_bowl = datetime(2026, 2, 8, 17, 30)  # 5:30 PM CT
    time_left = super_bowl - now
    hours_left = time_left.total_seconds() / 3600
    
    print(f"Current time: {now.strftime('%I:%M %p')}")
    print(f"Super Bowl kickoff: 5:30 PM CT")
    print(f"Time left: {hours_left:.1f} hours")
    
    if hours_left < 0.5:
        print("STATUS: CRITICAL - Less than 30 minutes!")
    elif hours_left < 1:
        print("STATUS: URGENT - Less than 1 hour!")
    
    print("\n" + "="*80)
    print("ALEMBIC FIX DEPLOYED: TESTING NOW")
    print("="*80)

if __name__ == "__main__":
    test_alembic_fix()
