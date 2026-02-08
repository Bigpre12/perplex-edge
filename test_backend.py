"""
Simple test to check if backend is responding
"""

import httpx

BASE_URL = "https://railway-engine-production.up.railway.app"

print("Testing backend endpoints...")
print()

# Test 1: Root endpoint
print(f"1. Testing {BASE_URL}/")
try:
    r = httpx.get(f"{BASE_URL}/", timeout=10)
    print(f"   Status: {r.status_code}")
    print(f"   Response: {r.text[:100]}")
except Exception as e:
    print(f"   Error: {e}")
print()

# Test 2: API health
print(f"2. Testing {BASE_URL}/api/health")
try:
    r = httpx.get(f"{BASE_URL}/api/health", timeout=10)
    print(f"   Status: {r.status_code}")
    print(f"   Response: {r.text[:100]}")
except Exception as e:
    print(f"   Error: {e}")
print()

# Test 3: Grading health
print(f"3. Testing {BASE_URL}/api/grading/health")
try:
    r = httpx.get(f"{BASE_URL}/api/grading/health", timeout=10)
    print(f"   Status: {r.status_code}")
    print(f"   Response: {r.text[:100]}")
except Exception as e:
    print(f"   Error: {e}")
print()

# Test 4: Simple endpoint check
print(f"4. Testing {BASE_URL}/api/grading/debug/picks-status")
try:
    r = httpx.get(f"{BASE_URL}/api/grading/debug/picks-status", timeout=10)
    print(f"   Status: {r.status_code}")
    print(f"   Response: {r.text[:200]}")
except Exception as e:
    print(f"   Error: {e}")
