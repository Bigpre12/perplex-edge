"""
Test grading endpoints
Run: python test_grading_endpoints.py
"""

import httpx
import time

BASE_URL = "https://perplex-edge-production.up.railway.app"

print("Testing grading endpoints...")
print("Waiting 30s for deployment...")
time.sleep(30)

# Test 1: Health endpoint (should work without DB)
print("\n1. Testing /api/grading/health...")
try:
    resp = httpx.get(f"{BASE_URL}/api/grading/health", timeout=30)
    print(f"   Status: {resp.status_code}")
    if resp.status_code == 200:
        print(f"   Response: {resp.json()}")
        print("   ✅ Health endpoint works!")
    else:
        print(f"   ❌ Error: {resp.text[:100]}")
except Exception as e:
    print(f"   ❌ Exception: {e}")

# Test 2: Debug picks status
print("\n2. Testing /api/grading/debug/picks-status...")
try:
    resp = httpx.get(f"{BASE_URL}/api/grading/debug/picks-status", timeout=30)
    print(f"   Status: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print(f"   Response: {data}")
        if data.get("nba_active", 0) == 0:
            print("   ⚠️  All picks are hidden - need to activate test picks")
        else:
            print(f"   ✅ Found {data.get('nba_active')} active picks")
    else:
        print(f"   ❌ Error: {resp.text[:100]}")
except Exception as e:
    print(f"   ❌ Exception: {e}")

# Test 3: Model status
print("\n3. Testing /api/grading/model-status...")
try:
    resp = httpx.get(f"{BASE_URL}/api/grading/model-status", timeout=30)
    print(f"   Status: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print(f"   Response: {data}")
        print("   ✅ Model status endpoint works!")
    else:
        print(f"   ❌ Error: {resp.text[:100]}")
except Exception as e:
    print(f"   ❌ Exception: {e}")

print("\n" + "="*50)
print("Testing complete!")
print("="*50)
