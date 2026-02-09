#!/usr/bin/env python3
"""
Test if CLV columns fix the picks endpoint
"""
import requests
import time

def test_clv_fix():
    """Test if CLV columns fix the picks endpoint"""
    base_url = "https://railway-engine-production.up.railway.app"
    
    print("TESTING IF CLV COLUMNS FIX THE PICKS ENDPOINT")
    print("="*80)
    
    print("\n1. You just ran these SQL commands:")
    print("   ALTER TABLE model_picks ADD COLUMN IF NOT EXISTS closing_odds NUMERIC(10, 4);")
    print("   ALTER TABLE model_picks ADD COLUMN IF NOT EXISTS clv_percentage NUMERIC(10, 4);")
    print("   ALTER TABLE model_picks ADD COLUMN IF NOT EXISTS roi_percentage NUMERIC(10, 4);")
    print("   ALTER TABLE model_picks ADD COLUMN IF NOT EXISTS opening_odds NUMERIC(10, 4);")
    print("   ALTER TABLE model_picks ADD COLUMN IF NOT EXISTS line_movement NUMERIC(10, 4);")
    print("   ALTER TABLE model_picks ADD COLUMN IF NOT EXISTS sharp_money_indicator NUMERIC(10, 4);")
    print("   ALTER TABLE model_picks ADD COLUMN IF NOT EXISTS best_book_odds NUMERIC(10, 4);")
    print("   ALTER TABLE model_picks ADD COLUMN IF NOT EXISTS best_book_name VARCHAR(50);")
    print("   ALTER TABLE model_picks ADD COLUMN IF NOT EXISTS ev_improvement NUMERIC(10, 4);")
    
    print("\n2. Waiting for database to update...")
    time.sleep(5)
    
    print("\n3. Testing NBA Picks Endpoint:")
    try:
        response = requests.get(f"{base_url}/api/sports/30/picks/player-props?limit=5", timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            props = data.get('items', [])
            print(f"   SUCCESS! Found {len(props)} NBA props")
            
            if props:
                print(f"   Sample NBA props:")
                for i, prop in enumerate(props[:3], 1):
                    player = prop.get('player', {})
                    print(f"   {i}. {player.get('name', 'N/A')}: {prop.get('stat_type', 'N/A')} {prop.get('line_value', 'N/A')}")
                    print(f"      Edge: {prop.get('edge', 0):.2%}")
                    print(f"      Confidence: {prop.get('confidence_score', 0):.1f}")
                    print(f"      Odds: {prop.get('odds', 0)}")
        elif response.status_code == 500:
            error_text = response.text
            print(f"   Still 500 error: {error_text[:100]}")
            if "does not exist" in error_text:
                print("   CLV columns may not have been added yet")
            else:
                print("   Different error - columns might be added")
        else:
            print(f"   Error: {response.text[:100]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n4. Testing NFL Super Bowl Picks:")
    try:
        response = requests.get(f"{base_url}/api/sports/31/picks/player-props?game_id=648&limit=5", timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            props = data.get('items', [])
            print(f"   SUCCESS! Found {len(props)} NFL props")
            
            if props:
                print(f"   Sample NFL props:")
                for i, prop in enumerate(props[:3], 1):
                    player = prop.get('player', {})
                    print(f"   {i}. {player.get('name', 'N/A')}: {prop.get('stat_type', 'N/A')} {prop.get('line_value', 'N/A')}")
                    print(f"      Edge: {prop.get('edge', 0):.2%}")
        else:
            print(f"   Error: {response.text[:100]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n5. Testing Parlay Builder:")
    try:
        parlay_url = f"{base_url}/api/sports/30/parlays/builder?leg_count=2&max_results=3"
        response = requests.get(parlay_url, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            parlays = data.get('parlays', [])
            print(f"   SUCCESS! Found {len(parlays)} parlays")
            
            if parlays:
                print(f"   Sample parlays:")
                for i, parlay in enumerate(parlays[:2], 1):
                    print(f"   {i}. EV: {parlay.get('total_ev', 0):.2%}")
                    print(f"      Legs: {len(parlay.get('legs', []))}")
                    print(f"      Model Status: {parlay.get('model_status', {}).get('status', 'N/A')}")
        else:
            print(f"   Error: {response.text[:100]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n6. Testing Frontend-Backend Connection:")
    try:
        response = requests.get("https://perplex-edge-production.up.railway.app/api/grading/model-status", timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"   SUCCESS: Frontend connected to backend!")
        elif response.status_code == 502:
            print(f"   502 Error: BACKEND_URL still needs fixing in frontend")
        else:
            print(f"   Status: {response.status_code}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n" + "="*80)
    print("TEST RESULTS:")
    print("="*80)
    
    print("\nNEXT STEPS:")
    print("1. If picks are working (200 status):")
    print("   - Great! CLV columns fixed the issue")
    print("   - Now fix frontend BACKEND_URL")
    print("   ")
    print("2. If picks still show 500 error:")
    print("   - Wait 30 seconds and try again")
    print("   - Database might still be updating")
    print("   ")
    print("3. If frontend shows 502:")
    print("   - Set BACKEND_URL in Railway frontend service")
    print("   - Value: https://railway-engine-production.up.railway.app")
    
    print("\n" + "="*80)
    print("CLV COLUMNS: ADDED MANUALLY")
    print("Testing if this fixes the picks issue...")
    print("="*80)

if __name__ == "__main__":
    test_clv_fix()
