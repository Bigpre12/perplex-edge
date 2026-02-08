#!/usr/bin/env python3
"""
Check database admin endpoints
"""
import requests

def check_db_admin():
    """Check database admin endpoints"""
    base_url = "https://railway-engine-production.up.railway.app"
    
    print("CHECKING DATABASE ADMIN ENDPOINTS")
    print("="*80)
    
    try:
        response = requests.get(f"{base_url}/openapi.json", timeout=10)
        data = response.json()
        
        paths = data.get("paths", {})
        db_paths = [path for path in paths if any(keyword in path.lower() for keyword in ['alembic', 'migration', 'database', 'db'])]
        
        print(f"\nFound {len(db_paths)} database-related endpoints:")
        for path in sorted(db_paths):
            methods = list(paths[path].keys())
            print(f"  {path} - {', '.join(methods)}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Try direct SQL execution
    print("\n2. Check if Direct SQL Endpoint Exists:")
    sql_url = f"{base_url}/admin/sql"
    
    try:
        response = requests.post(sql_url, json={"query": "SELECT column_name FROM information_schema.columns WHERE table_name = 'model_picks' ORDER BY ordinal_position"}, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Columns in model_picks: {data}")
        else:
            print(f"   Error: {response.text[:100]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    check_db_admin()
