import requests
import json

base_url = "http://127.0.0.1:8001"

def test_auth():
    # 1. Signup
    signup_data = {
        "username": "testuser_s25",
        "email": "test_s25@example.com",
        "password": "securepassword123"
    }
    print("Testing Signup...")
    r = requests.post(f"{base_url}/auth/signup", json=signup_data)
    print(f"Status: {r.status_code}")
    print(r.json())

    # 2. Login
    login_data = {
        "username": "testuser_s25",
        "password": "securepassword123"
    }
    print("\nTesting Login...")
    r = requests.post(f"{base_url}/auth/login", data=login_data)
    print(f"Status: {r.status_code}")
    resp = r.json()
    print(resp)
    
    if "access_token" in resp:
        token = resp["access_token"]
        print(f"\nLogin Successful! Token: {token[:20]}...")
    else:
        print("\nLogin Failed!")

if __name__ == "__main__":
    test_auth()
