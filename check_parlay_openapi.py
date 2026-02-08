#!/usr/bin/env python3
"""
Check parlay endpoints in OpenAPI
"""
import requests
import json

def check_parlay_in_openapi():
    """Check if parlay endpoints are in OpenAPI"""
    base_url = "https://railway-engine-production.up.railway.app"
    
    print("CHECKING PARLAY ENDPOINTS IN OPENAPI")
    print("="*80)
    
    try:
        response = requests.get(f"{base_url}/openapi.json", timeout=10)
        data = response.json()
        
        paths = data.get("paths", {})
        parlay_paths = [path for path in paths if "parlay" in path.lower()]
        
        print(f"\nFound {len(parlay_paths)} parlay-related endpoints:")
        for path in sorted(parlay_paths):
            methods = list(paths[path].keys())
            print(f"  {path} - {', '.join(methods)}")
        
        if not parlay_paths:
            print("\nWARNING: No parlay endpoints found!")
            print("Checking for 'public' endpoints...")
            public_paths = [path for path in paths if '/public/' in path]
            print(f"\nFound {len(public_paths)} public endpoints:")
            for path in sorted(public_paths)[:10]:
                methods = list(paths[path].keys())
                print(f"  {path} - {', '.join(methods)}")
            if len(public_paths) > 10:
                print(f"  ... and {len(public_paths) - 10} more")
        
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    check_parlay_in_openapi()
