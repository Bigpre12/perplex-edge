#!/usr/bin/env python3
"""
Test backend health using requests
"""
import requests
import json

def test_backend():
    """Test backend health"""
    url = "https://railway-engine-production.up.railway.app/health"
    
    print("Testing backend health...")
    print(f"URL: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("SUCCESS! Backend is responding")
            print(f"Response: {json.dumps(data, indent=2)}")
            return True
        else:
            print(f"HTTP {response.status_code}")
            try:
                print(f"Error: {response.json()}")
            except:
                print(f"Error: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    test_backend()
