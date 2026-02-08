#!/usr/bin/env python3
"""
Check deployment status
"""
import requests

def check_deployment():
    """Check deployment status"""
    base_url = "https://railway-engine-production.up.railway.app"
    
    print("CHECKING DEPLOYMENT STATUS")
    print("="*80)
    
    # Check health
    print("\n1. Health Check:")
    health_url = f"{base_url}/health"
    
    try:
        response = requests.get(health_url, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Health: {data}")
        else:
            print(f"   Error: {response.text[:100]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Check OpenAPI for new endpoint
    print("\n2. Check OpenAPI for Stub Endpoint:")
    openapi_url = f"{base_url}/openapi.json"
    
    try:
        response = requests.get(openapi_url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            paths = data.get("paths", {})
            
            stub_paths = [path for path in paths if "stub" in path.lower()]
            print(f"   Found {len(stub_paths)} stub endpoints:")
            for path in stub_paths:
                print(f"     {path}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    check_deployment()
