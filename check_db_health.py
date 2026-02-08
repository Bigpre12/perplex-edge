#!/usr/bin/env python3
"""
Check database health
"""
import requests

def check_db_health():
    """Check database health"""
    base_url = "https://railway-engine-production.up.railway.app"
    
    print("CHECKING DATABASE HEALTH")
    print("="*80)
    
    health_url = f"{base_url}/health/db"
    
    try:
        response = requests.get(health_url, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Database health: {data}")
        else:
            print(f"   Error: {response.text[:100]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    check_db_health()
