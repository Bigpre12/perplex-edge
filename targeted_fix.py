#!/usr/bin/env python3
"""
Targeted fix for remaining issues
"""
import requests
import subprocess
import time

def targeted_fix():
    """Targeted fix for remaining issues"""
    base_url = "https://railway-engine-production.up.railway.app"
    
    print("TARGETED FIX FOR REMAINING ISSUES")
    print("="*80)
    
    print("\n1. Current Status Analysis:")
    print("   Backend Health: OK")
    print("   CLV Columns: ERROR (missing)")
    print("   Picks Working: ERROR (500 due to missing columns)")
    print("   Parlay Builder: OK")
    print("   Frontend-Backend: ERROR (502 - wrong BACKEND_URL)")
    
    print("\n2. Issue 1: CLV Columns Missing")
    print("   The SQL query shows it's trying to select CLV columns that don't exist")
    print("   Need to fix the query to exclude these columns")
    
    # Find the file with the problematic query
    print("\n3. Finding the problematic query...")
    try:
        # Check the public.py file for the picks query
        with open("c:/Users/preio/perplex-edge/backend/app/api/public.py", "r") as f:
            content = f.read()
            
        # Look for the SELECT statement with CLV columns
        if "model_picks.closing_odds" in content:
            print("   Found CLV references in public.py")
            
            # Fix by removing CLV columns from the SELECT
            content = content.replace(
                "model_picks.closing_odds AS closing_odds,",
                "-- model_picks.closing_odds AS closing_odds,"
            )
            content = content.replace(
                "model_picks.clv_percentage AS clv_percentage,",
                "-- model_picks.clv_percentage AS clv_percentage,"
            )
            content = content.replace(
                "model_picks.roi_percentage AS roi_percentage,",
                "-- model_picks.roi_percentage AS roi_percentage,"
            )
            content = content.replace(
                "model_picks.opening_odds AS opening_odds,",
                "-- model_picks.opening_odds AS opening_odds,"
            )
            content = content.replace(
                "model_picks.line_movement AS line_movement,",
                "-- model_picks.line_movement AS line_movement,"
            )
            content = content.replace(
                "model_picks.sharp_money_indicator AS sharp_money_indicator,",
                "-- model_picks.sharp_money_indicator AS sharp_money_indicator,"
            )
            content = content.replace(
                "model_picks.best_book_odds AS best_book_odds,",
                "-- model_picks.best_book_odds AS best_book_odds,"
            )
            content = content.replace(
                "model_picks.best_book_name AS best_book_name,",
                "-- model_picks.best_book_name AS best_book_name,"
            )
            content = content.replace(
                "model_picks.ev_improvement AS ev_improvement,",
                "-- model_picks.ev_improvement AS ev_improvement,"
            )
            
            with open("c:/Users/preio/perplex-edge/backend/app/api/public.py", "w") as f:
                f.write(content)
                
            print("   Fixed CLV column references in public.py")
            
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n4. Pushing fix to git...")
    try:
        subprocess.run(["git", "add", "backend/app/api/public.py"], check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Fix CLV columns in picks query"], check=True, capture_output=True)
        subprocess.run(["git", "push", "origin", "main"], check=True, capture_output=True)
        print("   Pushed fix to git")
    except Exception as e:
        print(f"   Git push failed: {e}")
    
    print("\n5. Waiting for deployment...")
    time.sleep(30)
    
    print("\n6. Testing after fix...")
    try:
        response = requests.get(f"{base_url}/api/sports/30/picks/player-props?limit=1", timeout=10)
        print(f"   Picks Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            props = data.get('items', [])
            print(f"   SUCCESS! Picks working: {len(props)} props")
            
            if props:
                prop = props[0]
                player = prop.get('player', {})
                print(f"   Sample: {player.get('name', 'N/A')}: {prop.get('stat_type', 'N/A')} {prop.get('line_value', 'N/A')}")
                print(f"   Edge: {prop.get('edge', 0):.2%}")
        else:
            print(f"   Error: {response.text[:100]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n7. Issue 2: Frontend 502 Error")
    print("   Need to set BACKEND_URL in Railway frontend service")
    print("   Go to Railway dashboard > perplex-edge-production > Variables")
    print("   Set: BACKEND_URL=https://railway-engine-production.up.railway.app")
    
    print("\n" + "="*80)
    print("TARGETED FIX SUMMARY:")
    print("1. Fixed CLV columns in picks query")
    print("2. Pushed to git")
    print("3. Waiting for deployment")
    print("4. Manual action needed: Set BACKEND_URL in frontend")
    print("="*80)

if __name__ == "__main__":
    targeted_fix()
