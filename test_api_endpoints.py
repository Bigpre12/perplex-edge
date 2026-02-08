#!/usr/bin/env python3
"""
Test API endpoints
"""
import requests
import json

def test_api_endpoints():
    """Test various API endpoints"""
    base_url = "https://railway-engine-production.up.railway.app"
    
    endpoints = [
        "/health",
        "/api/health",
        "/api/grading/health",
        "/api/public/health",
    ]
    
    print("Testing API endpoints...")
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
                    print(f"  Response: {json.dumps(data, indent=4)}")
                except:
                    print(f"  Response: {response.text[:100]}")
            else:
                print(f"  Error: {response.text[:100]}")
        except requests.exceptions.RequestException as e:
            print(f"  Error: {e}")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    test_api_endpoints()
