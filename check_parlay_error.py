#!/usr/bin/env python3
"""
Check parlay builder error
"""
import requests

def check_parlay_error():
    """Check parlay builder error details"""
    base_url = "https://railway-engine-production.up.railway.app"
    
    print("CHECKING PARLAY BUILDER ERROR")
    print("="*80)
    
    # Try with minimal parameters
    url = f"{base_url}/api/sports/30/parlays/builder?leg_count=3&max_results=1"
    
    try:
        response = requests.get(url, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Error: {response.text}")
            
            # Try to get more details
            try:
                error_data = response.json()
                print(f"Error details: {json.dumps(error_data, indent=2)}")
            except:
                pass
    except Exception as e:
        print(f"Request error: {e}")
    
    print("="*80)

if __name__ == "__main__":
    check_parlay_error()
