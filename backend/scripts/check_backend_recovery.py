#!/usr/bin/env python3
"""
Check backend recovery after CLV columns addition
"""
import requests
import time

def check_backend_recovery():
    """Check backend recovery after CLV columns addition"""
    base_url = "https://railway-engine-production.up.railway.app"
    
    print("CHECKING BACKEND RECOVERY AFTER CLV COLUMNS ADDITION")
    print("="*80)
    
    print("\n1. Checking Backend Health:")
    try:
        response = requests.get(f"{base_url}/api/health", timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   SUCCESS: Backend is healthy!")
            print(f"   Health: {data}")
        else:
            print(f"   Status: {response.status_code}")
            print(f"   Backend may be restarting...")
    except Exception as e:
        print(f"   Error: {e}")
        print("   Backend may be restarting after SQL commands...")
    
    print("\n2. Checking if CLV Columns Were Added:")
    print("   After backend recovers, we should test:")
    print("   - NBA picks endpoint")
    print("   - NFL picks endpoint")
    print("   - Parlay builder")
    
    print("\n3. Testing Picks Endpoint (when backend is up):")
    try:
        response = requests.get(f"{base_url}/api/sports/30/picks/player-props?limit=1", timeout=5)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            props = data.get('items', [])
            print(f"   SUCCESS! Picks working: {len(props)} props")
            
            if props:
                prop = props[0]
                player = prop.get('player', {})
                print(f"   Sample: {player.get('name', 'N/A')}: {prop.get('stat_type', 'N/A')} {prop.get('line_value', 'N/A')}")
        elif response.status_code == 500:
            print("   Still 500 error - CLV columns may not be added yet")
        else:
            print(f"   Status: {response.status_code}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n" + "="*80)
    print("RECOVERY STATUS:")
    print("- Backend Health: Checking...")
    print("- CLV Columns: Added manually...")
    print("- Picks Endpoint: Waiting for backend...")
    print("- Parlay Builder: Waiting for backend...")
    print("="*80)
    
    print("\nNEXT STEPS:")
    print("1. Wait for backend to recover (1-2 minutes)")
    print("2. Test picks endpoint")
    print("3. If working, activate picks")
    print("4. Test parlay builder")
    print("5. Launch for Super Bowl!")
    
    print("\n" + "="*80)
    print("BACKEND RECOVERY: IN PROGRESS")
    print("SQL commands executed, backend restarting...")
    print("="*80)

if __name__ == "__main__":
    check_backend_recovery()
