#!/usr/bin/env python3
"""
Check admin endpoints
"""
import requests

def check_admin_endpoints():
    """Check admin endpoints"""
    base_url = "https://railway-engine-production.up.railway.app"
    
    print("CHECKING ADMIN ENDPOINTS")
    print("="*80)
    
    try:
        response = requests.get(f"{base_url}/openapi.json", timeout=10)
        data = response.json()
        
        paths = data.get("paths", {})
        admin_paths = [path for path in paths if "admin" in path.lower()]
        
        print(f"\nFound {len(admin_paths)} admin-related endpoints:")
        for path in sorted(admin_paths):
            methods = list(paths[path].keys())
            print(f"  {path} - {', '.join(methods)}")
            
        # Check for SQL endpoint specifically
        if "/admin/sql" in admin_paths:
            print("\n✅ SQL endpoint found!")
        else:
            print("\n❌ SQL endpoint not found")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    check_admin_endpoints()
