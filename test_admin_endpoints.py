"""
Test the new admin endpoints
Run: python test_admin_endpoints.py
"""

import httpx

BASE_URL = "https://perplex-edge-production.up.railway.app"

print("Testing admin endpoints...")
print()

# Test 1: Check picks status
print("1. Checking picks status...")
resp = httpx.get(f"{BASE_URL}/api/grading/debug/picks-status", timeout=30)
print(f"   Status: {resp.status_code}")
print(f"   Content-Type: {resp.headers.get('content-type', 'unknown')}")
if resp.status_code == 200 and 'application/json' in resp.headers.get('content-type', ''):
    data = resp.json()
    print(f"   Response: {data}")
else:
    print(f"   ERROR: Got HTML instead of JSON (deployment not ready)")
    print(f"   Preview: {resp.text[:100]}")
print()

# Test 2: Activate test picks
print("2. Activating test picks...")
resp = httpx.post(f"{BASE_URL}/api/grading/admin/activate-test-picks?count=100", timeout=30)
print(f"   Status: {resp.status_code}")
if resp.status_code == 200 and 'application/json' in resp.headers.get('content-type', ''):
    data = resp.json()
    print(f"   Response: {data}")
else:
    print(f"   ERROR: {resp.text[:100]}")
print()

# Test 3: Check model-status endpoint
print("3. Checking model-status...")
resp = httpx.get(f"{BASE_URL}/api/grading/model-status", timeout=30)
print(f"   Status: {resp.status_code}")
if resp.status_code == 200 and 'application/json' in resp.headers.get('content-type', ''):
    data = resp.json()
    print(f"   Status: {data.get('status')}")
    print(f"   Model Status: {data.get('model_status')}")
else:
    print(f"   ERROR: {resp.text[:100]}")
