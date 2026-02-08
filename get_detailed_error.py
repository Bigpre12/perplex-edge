#!/usr/bin/env python3
"""
Get detailed error info
"""
import requests

def get_detailed_error():
    """Get detailed error info"""
    base_url = "https://railway-engine-production.up.railway.app"
    
    print("GETTING DETAILED ERROR INFO")
    print("="*80)
    
    # Test with minimal parameters
    print("\n1. Minimal Props Test:")
    props_url = f"{base_url}/api/sports/31/picks/player-props?limit=1"
    
    try:
        response = requests.get(props_url, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"   Full Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test without any filters
    print("\n2. Test Without Filters:")
    props_url2 = f"{base_url}/api/sports/31/picks/player-props"
    
    try:
        response = requests.get(props_url2, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"   Full Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Check if the endpoint exists at all
    print("\n3. Check Endpoint Existence:")
    endpoint_url = f"{base_url}/api/sports/31/picks"
    
    try:
        response = requests.get(endpoint_url, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 404:
            print("   Endpoint doesn't exist")
        elif response.status_code != 200:
            print(f"   Error: {response.text[:200]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    get_detailed_error()
