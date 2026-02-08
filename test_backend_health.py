#!/usr/bin/env python3
"""
Simple test to check if backend is working
"""
import requests
import time

def test_backend():
    """Test backend health"""
    url = "https://railway-engine-production.up.railway.app/health"
    
    print("Testing backend health...")
    print(f"URL: {url}")
    
    for i in range(10):
        try:
            response = requests.get(url, timeout=5)
            print(f"Attempt {i+1}: Status {response.status_code}")
            
            if response.status_code == 200:
                print("SUCCESS! Backend is responding")
                print(f"Response: {response.json()}")
                return True
            else:
                print(f"HTTP {response.status_code}: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"Attempt {i+1}: Error - {e}")
        
        if i < 9:
            print("Waiting 30 seconds before next attempt...")
            time.sleep(30)
    
    print("FAILED: Backend not responding after 10 attempts")
    return False

if __name__ == "__main__":
    test_backend()
