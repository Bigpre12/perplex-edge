#!/usr/bin/env python3
"""
Find working odds endpoints
"""
import requests

def find_odds_endpoints():
    """Find working odds endpoints"""
    base_url = "https://railway-engine-production.up.railway.app"
    
    print("FINDING WORKING ODDS ENDPOINTS")
    print("="*80)
    
    # Get all endpoints with 'odds' in them
    try:
        response = requests.get(f"{base_url}/openapi.json", timeout=10)
        data = response.json()
        
        paths = data.get("paths", {})
        odds_paths = [path for path in paths if "odds" in path.lower()]
        
        print(f"\nFound {len(odds_paths)} odds-related endpoints:")
        for path in sorted(odds_paths):
            methods = list(paths[path].keys())
            print(f"  {path} - {', '.join(methods)}")
            
            # Test a few
            if len(odds_paths) <= 5:
                for method in methods:
                    if method.upper() == 'GET':
                        try:
                            test_response = requests.get(f"{base_url}{path}", timeout=5)
                            print(f"    Test: {test_response.status_code}")
                            if test_response.status_code == 200:
                                print(f"      Working!")
                            break
                        except:
                            print(f"    Test: Error")
                            break
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    find_odds_endpoints()
