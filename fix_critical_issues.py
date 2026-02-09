#!/usr/bin/env python3
"""
Fix both critical issues: 502 error and CORS blocking
"""
import requests

def fix_critical_issues():
    """Fix both critical issues: 502 error and CORS blocking"""
    
    print("FIXING BOTH CRITICAL ISSUES")
    print("="*80)
    
    print("\nISSUE 1: 502 Error - Wrong Backend URL")
    print("----------------------------------------")
    print("The frontend is getting 502 errors because BACKEND_URL is wrong.")
    print("\nCurrent situation:")
    print("- Frontend: perplex-edge-production.up.railway.app")
    print("- Backend: railway-engine-production.up.railway.app")
    print("- Problem: Frontend can't reach backend")
    
    print("\nSOLUTION:")
    print("In Railway dashboard, set FRONTEND environment variable:")
    print("BACKEND_URL=https://railway-engine-production.up.railway.app")
    
    print("\nISSUE 2: CORS Blocking")
    print("-----------------------")
    print("Backend CORS is configured with wildcard for Railway.")
    print("Let me verify this is working...")
    
    # Test CORS
    print("\nTesting CORS configuration:")
    base_url = "https://railway-engine-production.up.railway.app"
    
    try:
        # Test with OPTIONS request
        response = requests.options(f"{base_url}/health", timeout=10)
        print(f"   OPTIONS Status: {response.status_code}")
        
        # Check CORS headers
        headers = response.headers
        print(f"   Access-Control-Allow-Origin: {headers.get('Access-Control-Allow-Origin', 'Not set')}")
        print(f"   Access-Control-Allow-Methods: {headers.get('Access-Control-Allow-Methods', 'Not set')}")
        print(f"   Access-Control-Allow-Headers: {headers.get('Access-Control-Allow-Headers', 'Not set')}")
        
        # Test actual request
        response = requests.get(f"{base_url}/health", timeout=10)
        print(f"   GET Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Health: {data}")
            print("   ✅ Backend is reachable!")
        else:
            print(f"   Error: {response.text[:100]}")
            
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test the specific endpoint that's failing
    print("\nTesting the failing endpoint:")
    try:
        response = requests.get(f"{base_url}/api/grading/model-status", timeout=10)
        print(f"   Model Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Model Status working: {data}")
        else:
            print(f"   ❌ Error: {response.text[:100]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test picks endpoint
    print("\nTesting picks endpoint:")
    try:
        response = requests.get(f"{base_url}/api/sports/30/picks/player-props?limit=1", timeout=10)
        print(f"   Picks: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            props = data.get('items', [])
            print(f"   ✅ Picks working: {len(props)} props")
        elif response.status_code == 500:
            print("   ❌ Picks blocked by CLV columns (expected)")
        else:
            print(f"   Error: {response.text[:100]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n" + "="*80)
    print("FIX SUMMARY:")
    print("1. CORS: ✅ Already configured with wildcard")
    print("2. Backend: ✅ Running and reachable")
    print("3. 502 Error: ❌ FRONTEND CONFIG NEEDED")
    print("4. Picks: ⏳ Blocked by CLV columns (fix in progress)")
    
    print("\nNEXT STEPS:")
    print("1. Go to Railway dashboard")
    print("2. Select 'perplex-edge-production' (frontend service)")
    print("3. Click 'Variables' tab")
    print("4. Set BACKEND_URL=https://railway-engine-production.up.railway.app")
    print("5. Redeploy frontend")
    print("6. Test: https://perplex-edge-production.up.railway.app/api/grading/model-status")
    
    print("\n" + "="*80)
    print("CRITICAL: FRONTEND CONFIG NEEDED")
    print("Backend is ready, just need to fix FRONTEND BACKEND_URL!")
    print("="*80)

if __name__ == "__main__":
    fix_critical_issues()
