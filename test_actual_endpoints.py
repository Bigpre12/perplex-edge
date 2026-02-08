#!/usr/bin/env python3
"""
Test actual API endpoints
"""
import requests
import json

def test_actual_endpoints():
    """Test actual API endpoints"""
    base_url = "https://railway-engine-production.up.railway.app"
    
    endpoints = [
        ("/api/sports", "Get sports"),
        ("/api/tonight/summary", "Tonight's summary"),
        ("/api/players/hot-cold", "Hot/cold players"),
        ("/admin/season-info", "Season info"),
        ("/sports", "Sports (no prefix)"),
    ]
    
    print("Testing actual API endpoints...")
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
                        if 'status' in data:
                            print(f"  Status: {data.get('status')}")
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
    test_actual_endpoints()
