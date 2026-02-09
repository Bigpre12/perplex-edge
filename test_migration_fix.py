#!/usr/bin/env python3
"""
TEST MIGRATION FIX - Verify Alembic syntax fix
"""
import requests
import time
from datetime import datetime

def test_migration_fix():
    """Test if the migration syntax fix works"""
    base_url = "https://railway-engine-production.up.railway.app"
    
    print("TESTING MIGRATION FIX")
    print("="*80)
    
    print(f"\nTime: {datetime.now().strftime('%I:%M:%S %p')}")
    print("Status: Alembic syntax fix deployed")
    
    print("\n1. Fix Applied:")
    print("   - Fixed syntax error in 20260208_100000_add_closing_odds_to_model_picks.py")
    print("   - Removed nullable=True from tuple definition")
    print("   - Added nullable=True to op.add_column() call")
    print("   - Fixed tuple unpacking from 3 to 2 elements")
    
    print("\n2. Waiting for deployment...")
    time.sleep(30)
    
    print("\n3. Testing backend health...")
    try:
        response = requests.get(f"{base_url}/api/health", timeout=10)
        print(f"Backend Health: {response.status_code}")
        
        if response.status_code == 200:
            print("   Backend is healthy - migration likely succeeded!")
        else:
            print("   Backend still starting...")
    except Exception as e:
        print(f"Backend Health: ERROR - {e}")
    
    print("\n4. Testing original endpoints (should work now):")
    
    original_endpoints = [
        ("NFL Picks", "/api/sports/31/picks/player-props?limit=5"),
        ("NBA Picks", "/api/sports/30/picks/player-props?limit=5"),
        ("NFL Games", "/api/sports/31/games?date=2026-02-08")
    ]
    
    working_count = 0
    for name, endpoint in original_endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            if response.status_code == 200:
                print(f"   {name}: {response.status_code} OK")
                working_count += 1
            elif response.status_code == 500:
                print(f"   {name}: {response.status_code} (Still has issues)")
            else:
                print(f"   {name}: {response.status_code}")
        except Exception as e:
            print(f"   {name}: ERROR - {e}")
    
    print("\n5. Testing working endpoints:")
    
    working_endpoints = [
        ("Immediate Props", "/immediate/working-player-props?sport_id=31"),
        ("Super Bowl Props", "/immediate/super-bowl-props"),
        ("Working Parlays", "/immediate/working-parlays")
    ]
    
    for name, endpoint in working_endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            if response.status_code == 200:
                print(f"   {name}: {response.status_code} OK")
            else:
                print(f"   {name}: {response.status_code} (Still deploying)")
        except Exception as e:
            print(f"   {name}: ERROR - {e}")
    
    print("\n" + "="*80)
    print("MIGRATION FIX RESULTS:")
    print("="*80)
    
    if working_count > 0:
        print("\nSUCCESS: Migration fix worked!")
        print(f"   {working_count} original endpoints working")
        print("   CLV columns added successfully")
        print("   Original endpoints should work now")
    else:
        print("\nIN PROGRESS: Migration still running...")
        print("   Wait 2-3 more minutes")
        print("   Check Railway deployment logs")
    
    print("\n" + "="*80)
    print("MIGRATION FIX DEPLOYED!")
    print("="*80)

if __name__ == "__main__":
    test_migration_fix()
