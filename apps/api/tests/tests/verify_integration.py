import requests
import time
import sys

BASE_URL = "http://localhost:8000"

def test_endpoint(name, url, expected_status=200):
    print(f"Testing {name} ({url})...")
    try:
        response = requests.get(f"{BASE_URL}{url}")
        if response.status_code == expected_status:
            print(f"PASS: {name} returned {response.status_code}")
            return True, response.json()
        else:
            print(f"FAIL: {name} returned {response.status_code}")
            print(response.text[:200])
            return False, None
    except Exception as e:
        print(f"FAIL: {name} error: {e}")
        return False, None

def main():
    print("Verifying Integration...")
    
    # 1. Health Check
    success, data = test_endpoint("Health", "/health")
    if not success:
        print("Skipping other tests due to health check failure.")
        return

    # 2. Monte Carlo
    success, data = test_endpoint("Monte Carlo", "/analysis/monte-carlo-simulation?game_id=648&simulations=100")
    if success and 'results' in data:
        print("PASS: Monte Carlo data structure verified")
    else:
        print("FAIL: Monte Carlo data missing")

    # 3. Picks Stats (CLV)
    # Note: Requires DB connection, might fail if DB not set up, but we want to see if endpoint is reachable
    success, data = test_endpoint("Picks Stats", "/picks/stats?hours=24")
    if success:
        if 'clv_stats' in data:
             print("PASS: CLV stats present")
        else:
             print("WARN: CLV stats missing (data might be empty)")

    # 4. High EV Picks
    success, data = test_endpoint("High EV Picks", "/picks/high-ev?min_ev=1.0")
    if success:
        print(f"PASS: Found {len(data)} high EV picks")

if __name__ == "__main__":
    main()
