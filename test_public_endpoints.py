#!/usr/bin/env python3
"""
Test public endpoints
"""
import requests
import json

def test_public_endpoints():
    """Test public API endpoints"""
    base_url = "https://railway-engine-production.up.railway.app"
    
    endpoints = [
        "/api/public/sports",
        "/api/public/markets",
        "/api/public/games/1",
        "/api/sportsbook_intelligence/signals",
        "/api/sportsbook_intelligence/intelligence",
    ]
    
    print("Testing public endpoints...")
    print("="*80)
    
    for endpoint in endpoints:
        url = base_url + endpoint
        print(f"\nTesting: {endpoint}")
        
        try:
            response = requests.get(url, timeout=5)
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, list):
                        print(f"  Response: List with {len(data)} items")
                    else:
                        print(f"  Response: {json.dumps(data, indent=4)[:200]}...")
                except:
                    print(f"  Response: {response.text[:100]}")
            else:
                print(f"  Error: {response.text[:100]}")
        except requests.exceptions.RequestException as e:
            print(f"  Error: {e}")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    test_public_endpoints()
