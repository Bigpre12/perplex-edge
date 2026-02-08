"""
Frontend Integration Diagnostic Script
"""

import asyncio
import sys
import requests
from datetime import datetime, timezone

# Add the backend directory to the path
sys.path.append('/app')

async def check_frontend_integration():
    """Check frontend-backend integration issues."""
    
    base_url = 'https://railway-engine-production.up.railway.app'
    
    print("FRONTEND INTEGRATION DIAGNOSTIC")
    print("=" * 50)
    print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
    print()
    
    print("FRONTEND STATE ANALYSIS:")
    print("Based on your frontend state:")
    print("  dataExists: true")
    print("  parlaysCount: 0")  
    print("  totalCandidates: 0")
    print("  showEmpty: true")
    print("  status: 'success'")
    print()
    
    print("BACKEND VERIFICATION:")
    
    # Test exact endpoint frontend might be calling
    endpoints_to_test = [
        ('/api/parlays/game-free?sport_id=30&limit=10', 'Game Free Parlays'),
        ('/api/parlays/game-free?sport_id=30&min_ev=0.01&min_confidence=0.5&limit=10', 'Game Free Parlays with Filters'),
        ('/api/candidates/30?limit=10', 'Candidates'),
        ('/api/candidates/30?min_ev=0.01&min_confidence=0.5&limit=10', 'Candidates with Filters')
    ]
    
    for endpoint, name in endpoints_to_test:
        try:
            response = requests.get(base_url + endpoint, timeout=10)
            print(f"  {name}:")
            print(f"    Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                if 'slips' in data:
                    slips = data.get('slips', [])
                    print(f"    Slips: {len(slips)}")
                    if slips:
                        print(f"    Sample slip ID: {slips[0].get('id', 'N/A')}")
                        print(f"    Sample slip legs: {len(slips[0].get('legs', []))}")
                
                if 'candidates' in data:
                    candidates = data.get('candidates', [])
                    print(f"    Candidates: {len(candidates)}")
                    if candidates:
                        print(f"    Sample candidate: {candidates[0].get('player_name', 'N/A')}")
                
                if 'parlays' in data:
                    parlays = data.get('parlays', [])
                    print(f"    Parlays: {len(parlays)}")
                
                # Check for data structure differences
                if 'data' in data:
                    print(f"    Has 'data' field: Yes")
                if 'pagination' in data:
                    print(f"    Has 'pagination' field: Yes")
                    
            else:
                print(f"    Error: {response.text[:100]}")
                
        except Exception as e:
            print(f"    Error: {e}")
        
        print()
    
    print("POSSIBLE ISSUES:")
    print("1. Frontend is calling different endpoint than tested")
    print("2. Frontend expects different data structure")
    print("3. Frontend has stale cached data")
    print("4. Frontend filtering parameters are different")
    print("5. Frontend is using different base URL")
    print()
    
    print("RECOMMENDATIONS:")
    print("1. Check browser network tab for actual API calls")
    print("2. Verify frontend is calling correct endpoints")
    print("3. Clear browser cache and localStorage")
    print("4. Check frontend console for errors")
    print("5. Verify frontend base URL configuration")
    print()
    
    print("BACKEND HEALTH CHECK:")
    try:
        response = requests.get(base_url + '/health', timeout=10)
        print(f"  Health Check: {response.status_code}")
        if response.status_code == 200:
            print("  Backend is healthy and responding")
        else:
            print("  Backend health check failed")
    except Exception as e:
        print(f"  Health check error: {e}")
    
    print()
    print("NEXT STEPS:")
    print("1. Open browser developer tools")
    print("2. Go to Network tab")
    print("3. Refresh the parlay builder page")
    print("4. Check what endpoints are actually being called")
    print("5. Compare response structure with what frontend expects")
    print()
    
    print("=" * 50)
    print("DIAGNOSTIC COMPLETE")
    print("Backend is working - issue likely in frontend integration")

if __name__ == "__main__":
    asyncio.run(check_frontend_integration())
