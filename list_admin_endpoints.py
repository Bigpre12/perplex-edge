#!/usr/bin/env python3
"""
List available admin endpoints
"""
import requests

def list_admin_endpoints():
    """List available admin endpoints"""
    base_url = "https://railway-engine-production.up.railway.app"
    
    print("CHECKING AVAILABLE ADMIN ENDPOINTS")
    print("="*80)
    
    try:
        response = requests.get(f"{base_url}/openapi.json", timeout=10)
        data = response.json()
        
        paths = data.get("paths", {})
        admin_paths = [path for path in paths if "admin" in path.lower()]
        
        print(f"\nFound {len(admin_paths)} admin endpoints:")
        for path in sorted(admin_paths)[:10]:
            methods = list(paths[path].keys())
            print(f"  {path} - {', '.join(methods)}")
        
        if len(admin_paths) > 10:
            print(f"  ... and {len(admin_paths) - 10} more")
            
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    list_admin_endpoints()
