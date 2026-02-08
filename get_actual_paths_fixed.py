#!/usr/bin/env python3
"""
Get actual API paths
"""
import requests
import json

def get_actual_paths():
    """Get actual API paths from OpenAPI"""
    base_url = "https://railway-engine-production.up.railway.app"
    
    print("Getting actual API paths...")
    print("="*80)
    
    try:
        response = requests.get(f"{base_url}/openapi.json", timeout=10)
        data = response.json()
        
        paths = data.get("paths", {})
        
        # Group by category
        categories = {}
        for path, methods in paths.items():
            category = path.split("/")[1] if len(path.split("/")) > 1 else "root"
            if category not in categories:
                categories[category] = []
            categories[category].append((path, list(methods.keys())))
        
        print(f"Found {len(paths)} endpoints in {len(categories)} categories:\n")
        
        for category, endpoints in sorted(categories.items()):
            print(f"{category.upper()} ({len(endpoints)} endpoints):")
            for path, methods in endpoints[:5]:  # Show first 5
                print(f"  {path} - {', '.join(methods)}")
            if len(endpoints) > 5:
                print(f"  ... and {len(endpoints) - 5} more")
            print()
        
        # Test a few endpoints
        test_paths = [
            "/health",
            "/api/health",
        ]
        
        print("Testing basic endpoints:")
        for path in test_paths:
            if path in paths:
                try:
                    resp = requests.get(f"{base_url}{path}", timeout=5)
                    print(f"  {path}: {resp.status_code}")
                except:
                    print(f"  {path}: Error")
        
    except Exception as e:
        print(f"Error: {e}")
    
    print("="*80)

if __name__ == "__main__":
    get_actual_paths()
