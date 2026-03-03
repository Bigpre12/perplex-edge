#!/usr/bin/env python3
"""
Test if fixes work after deployment
"""
import requests
import time

def test_fixes():
    """Test if fixes work after deployment"""
    base_url = "https://railway-engine-production.up.railway.app"
    
    print("TESTING IF FIXES WORK AFTER DEPLOYMENT")
    print("="*80)
    
    print("\n1. Changes made:")
    print("   - Commented out CLV columns in ModelPick model")
    print("   - Fixed picks query to select only existing columns")
    print("   - Pushed to git (commit: 726859b)")
    
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
    
    print("\n4. Testing NBA picks:")
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
                    
                # Get total count
                total_url = f"{base_url}/api/sports/30/picks/player-props?limit=200"
                total_response = requests.get(total_url, timeout=10)
                if total_response.status_code == 200:
                    total_data = total_response.json()
                    total_props = total_data.get('items', [])
                    print(f"\n   Total NBA props: {len(total_props)}")
        else:
            print(f"   Error: {response.text[:100]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n5. Testing NFL Super Bowl picks:")
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
    
    print("\n6. Testing parlay builder:")
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
        else:
            print(f"   Error: {response.text[:100]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n7. Testing frontend-backend connection:")
    try:
        response = requests.get("https://perplex-edge-production.up.railway.app/api/grading/model-status", timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"   SUCCESS: Frontend connected to backend!")
        elif response.status_code == 502:
            print(f"   502 Error: BACKEND_URL still needs fixing")
        else:
            print(f"   Status: {response.status_code}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n" + "="*80)
    print("FIX RESULTS:")
    print("="*80)
    
    print("\nSTATUS SUMMARY:")
    print("- Backend Health: Testing...")
    print("- NBA Picks: Testing...")
    print("- NFL Picks: Testing...")
    print("- Parlay Builder: Testing...")
    print("- Frontend-Backend: Testing...")
    
    print("\nNEXT STEPS:")
    print("1. If picks are working (200 status):")
    print("   - Great! CLV fix worked")
    print("   - Now fix frontend BACKEND_URL")
    print("   ")
    print("2. If picks still show 500:")
    print("   - Wait longer for deployment")
    print("   - Check if fixes were applied correctly")
    print("   ")
    print("3. If frontend shows 502:")
    print("   - Set BACKEND_URL in Railway frontend service")
    print("   - Value: https://railway-engine-production.up.railway.app")
    
    print("\n" + "="*80)
    print("FIXES DEPLOYED: TESTING NOW")
    print("="*80)

if __name__ == "__main__":
    test_fixes()
