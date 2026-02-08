#!/usr/bin/env python3
"""
Check NFL endpoints
"""
import requests

def check_nfl_endpoints():
    """Check NFL endpoints"""
    base_url = "https://railway-engine-production.up.railway.app"
    
    print("CHECKING NFL ENDPOINTS")
    print("="*80)
    
    try:
        response = requests.get(f"{base_url}/openapi.json", timeout=10)
        data = response.json()
        
        paths = data.get("paths", {})
        nfl_paths = [path for path in paths if "nfl" in path.lower()]
        
        print(f"\nFound {len(nfl_paths)} NFL-related endpoints:")
        for path in sorted(nfl_paths):
            methods = list(paths[path].keys())
            print(f"  {path} - {', '.join(methods)}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    check_nfl_endpoints()
