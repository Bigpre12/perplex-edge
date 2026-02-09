#!/usr/bin/env python3
"""
Execute the fix immediately - set BACKEND_URL and test
"""
import requests

def execute_fix():
    """Execute the fix immediately - set BACKEND_URL and test"""
    
    print("EXECUTING THE FIX IMMEDIATELY")
    print("="*80)
    
    print("\nSTEP 1: SET BACKEND_URL IN FRONTEND SERVICE")
    print("=========================================")
    print("Go to Railway Dashboard:")
    print("1. Go to https://railway.app/dashboard")
    print("2. Click your project")
    print("3. Click 'perplex-edge-production' service (frontend)")
    print("4. Click 'Variables' tab")
    print("5. Click 'New Variable'")
    print("6. Set:")
    print("   - Name: BACKEND_URL")
    print("   - Value: https://railway-engine-production.up.railway.app")
    print("7. Click 'Add'")
    print("\nRailway will automatically redeploy (2-3 minutes)")
    
    print("\nSTEP 2: WAIT FOR DEPLOY AND TEST")
    print("==================================")
    print("After frontend redeploys, test these URLs:")
    
    base_url = "https://railway-engine-production.up.railway.app"
    frontend_url = "https://perplex-edge-production.up.railway.app"
    
    print(f"\nTest 1: Backend health directly")
    print(f"{base_url}/api/health")
    print("Expected: {'status': 'healthy'}")
    
    print(f"\nTest 2: Frontend proxy to backend")
    print(f"{frontend_url}/api/grading/model-status")
    print("Expected: JSON response (not 502)")
    
    print(f"\nTest 3: Picks endpoint")
    print(f"{frontend_url}/api/sports/30/picks/player-props")
    print("Expected: JSON array or CLV error")
    
    print("\nSTEP 3: CURRENT STATUS CHECK")
    print("=============================")
    
    # Test backend health
    print("\nTesting backend health...")
    try:
        response = requests.get(f"{base_url}/api/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend health: {data}")
        else:
            print(f"❌ Backend health error: {response.status_code}")
    except Exception as e:
        print(f"❌ Backend health error: {e}")
    
    # Test model status endpoint
    print("\nTesting model status endpoint...")
    try:
        response = requests.get(f"{base_url}/api/grading/model-status", timeout=10)
        print(f"Model Status (direct): {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Model Status working: {data}")
        elif response.status_code == 404:
            print("ℹ️ Model Status endpoint not found (different issue)")
        else:
            print(f"❌ Model Status error: {response.text[:100]}")
    except Exception as e:
        print(f"❌ Model Status error: {e}")
    
    # Test picks endpoint
    print("\nTesting picks endpoint...")
    try:
        response = requests.get(f"{base_url}/api/sports/30/picks/player-props?limit=1", timeout=10)
        print(f"Picks Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            props = data.get('items', [])
            print(f"✅ Picks working: {len(props)} props")
        elif response.status_code == 500:
            print("⏳ Picks blocked by CLV columns (expected)")
            print("   Need to add CLV columns")
        else:
            print(f"❌ Picks error: {response.text[:100]}")
    except Exception as e:
        print(f"❌ Picks error: {e}")
    
    print("\nSTEP 4: CLV COLUMNS STATUS")
    print("=======================")
    print("The picks endpoint shows 500 error due to missing CLV columns.")
    print("Quick fix options:")
    print("\nOption 1: Add columns via SQL (when SQL endpoint is deployed)")
    print("ALTER TABLE model_picks ADD COLUMN IF NOT EXISTS clv_percentage NUMERIC(10, 4);")
    print("ALTER TABLE model_picks ADD COLUMN IF NOT EXISTS closing_odds NUMERIC(10, 4);")
    
    print("\nOption 2: Make columns optional in code")
    print("clv_percentage = getattr(pick, 'clv_percentage', None)")
    print("closing_odds = getattr(pick, 'closing_odds', None)")
    
    print("\nSTEP 5: TIMELINE")
    print("============")
    import datetime
    now = datetime.datetime.now()
    super_bowl = datetime.datetime(2026, 2, 8, 17, 30)  # 5:30 PM CT
    time_left = super_bowl - now
    hours_left = time_left.total_seconds() / 3600
    
    print(f"Current time: {now.strftime('%I:%M %p')}")
    print(f"Super Bowl kickoff: 5:30 PM CT")
    print(f"Time left: {hours_left:.1f} hours")
    
    if hours_left > 6:
        print("Status: Plenty of time")
    elif hours_left > 3:
        print("Status: Good time")
    else:
        print("Status: Getting tight")
    
    print("\n" + "="*80)
    print("EXECUTION PLAN:")
    print("1. Set BACKEND_URL in Railway dashboard (doing now)")
    print("2. Wait 3 minutes for redeploy")
    print("3. Test frontend proxy")
    print("4. Fix CLV columns")
    print("5. Activate picks")
    print("6. Test full system")
    print("="*80)
    
    print("\nACTION REQUIRED:")
    print("Go to Railway dashboard NOW and set BACKEND_URL!")
    print("Then report back in 3 minutes.")

if __name__ == "__main__":
    execute_fix()
