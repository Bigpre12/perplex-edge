#!/usr/bin/env python3
"""
Test parlay endpoints with correct URLs
"""
import requests
import json

def test_parlay_endpoints_correct():
    """Test parlay endpoints with correct URLs"""
    base_url = "https://railway-engine-production.up.railway.app"
    
    print("TESTING PARLAY ENDPOINTS (CORRECT URLS)")
    print("="*80)
    
    endpoints = [
        ("/api/sports/1/parlays/builder?leg_count=3", "Parlay Builder"),
        ("/api/sports/1/parlays/auto-generate?leg_count=4", "Auto Generate"),
        ("/api/parlays/odds-health?sport_id=1", "Odds Health"),
    ]
    
    for endpoint, desc in endpoints:
        url = base_url + endpoint
        print(f"\n{desc}: {endpoint}")
        
        try:
            response = requests.get(url, timeout=10)
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, dict):
                        if "parlays" in data:
                            print(f"  Success: Found {len(data.get('parlays', []))} parlays")
                        elif "slips" in data:
                            print(f"  Success: Found {len(data.get('slips', []))} slips")
                        elif "status" in data:
                            print(f"  Success: Status {data.get('status')}")
                        else:
                            print(f"  Success: {len(data)} keys")
                            print(f"  Keys: {list(data.keys())[:5]}")
                    elif isinstance(data, list):
                        print(f"  Success: List with {len(data)} items")
                    else:
                        print(f"  Success: {str(data)[:100]}")
                except:
                    print(f"  Response: {response.text[:100]}")
            else:
                print(f"  Error: {response.text[:100]}")
        except requests.exceptions.RequestException as e:
            print(f"  Error: {e}")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    test_parlay_endpoints_correct()
