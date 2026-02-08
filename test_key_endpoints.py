#!/usr/bin/env python3
"""
Test key endpoints
"""
import requests
import json

def test_key_endpoints():
    """Test key API endpoints"""
    base_url = "https://railway-engine-production.up.railway.app"
    
    endpoints = [
        ("/api/public/sports", "Get sports"),
        ("/api/public/games/1", "Get games for sport 1"),
        ("/api/sportsbook_intelligence/intelligence", "Sportsbook intelligence"),
        ("/api/sportsbook_intelligence/signals", "Trading signals"),
        ("/api/admin/season-info", "Season info"),
    ]
    
    print("Testing key endpoints...")
    print("="*80)
    
    for endpoint, desc in endpoints:
        url = base_url + endpoint
        print(f"\n{desc}: {endpoint}")
        
        try:
            response = requests.get(url, timeout=5)
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, list):
                        print(f"  Success: List with {len(data)} items")
                        if data:
                            print(f"  Sample: {json.dumps(data[0], indent=2)[:200]}...")
                    elif isinstance(data, dict):
                        print(f"  Success: {len(data)} keys")
                        print(f"  Keys: {list(data.keys())[:5]}")
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
    test_key_endpoints()
