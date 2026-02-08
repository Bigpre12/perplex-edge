#!/usr/bin/env python3
"""
Check available endpoints
"""
import requests
import json

def check_docs():
    """Check API docs"""
    base_url = "https://railway-engine-production.up.railway.app"
    
    docs_endpoints = [
        "/docs",
        "/redoc",
        "/openapi.json",
    ]
    
    print("Checking API documentation...")
    print("="*80)
    
    for endpoint in docs_endpoints:
        url = base_url + endpoint
        print(f"\nChecking: {endpoint}")
        
        try:
            response = requests.get(url, timeout=5)
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                if endpoint == "/openapi.json":
                    data = response.json()
                    paths = data.get("paths", {})
                    print(f"  Found {len(paths)} endpoints:")
                    for path in list(paths.keys())[:10]:
                        print(f"    - {path}")
                    if len(paths) > 10:
                        print(f"    ... and {len(paths) - 10} more")
                else:
                    print(f"  Documentation available at {endpoint}")
            else:
                print(f"  Not available")
        except requests.exceptions.RequestException as e:
            print(f"  Error: {e}")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    check_docs()
