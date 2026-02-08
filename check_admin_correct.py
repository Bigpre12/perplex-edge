#!/usr/bin/env python3
"""
Check correct admin endpoints
"""
import requests

def check_admin_correct():
    """Check correct admin endpoints"""
    base_url = "https://railway-engine-production.up.railway.app"
    
    print("CHECKING CORRECT ADMIN ENDPOINTS")
    print("="*80)
    
    # Check admin quota
    print("\n1. Admin Quota:")
    quota_url = f"{base_url}/admin/quota"
    
    try:
        response = requests.get(quota_url, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Quota info: {data}")
        else:
            print(f"   Error: {response.text[:100]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Check admin cache clear
    print("\n2. Admin Cache Clear:")
    cache_url = f"{base_url}/admin/cache/clear"
    
    try:
        response = requests.post(cache_url, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Cache cleared: {data}")
        else:
            print(f"   Error: {response.text[:100]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Check admin jobs
    print("\n3. Admin Jobs:")
    jobs_url = f"{base_url}/admin/jobs/sync-quota-safe"
    
    try:
        response = requests.post(jobs_url, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Job triggered: {data}")
        else:
            print(f"   Error: {response.text[:100]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    check_admin_correct()
