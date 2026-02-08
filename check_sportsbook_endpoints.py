#!/usr/bin/env python3
"""
Check available sportsbook endpoints
"""
import requests

def check_sportsbook_endpoints():
    """Check available sportsbook endpoints"""
    base_url = "https://railway-engine-production.up.railway.app"
    
    print("CHECKING AVAILABLE SPORTSBOOK ENDPOINTS")
    print("="*80)
    
    try:
        response = requests.get(f"{base_url}/openapi.json", timeout=10)
        data = response.json()
        
        paths = data.get("paths", {})
        sportsbook_paths = [path for path in paths if "sportsbook" in path.lower()]
        
        print(f"\nFound {len(sportsbook_paths)} sportsbook-related endpoints:")
        for path in sorted(sportsbook_paths):
            methods = list(paths[path].keys())
            print(f"  {path} - {', '.join(methods)}")
            
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    check_sportsbook_endpoints()
