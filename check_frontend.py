#!/usr/bin/env python3
"""
Check frontend status and identify issues
"""
import subprocess
import sys
import os

def check_frontend():
    """Check frontend status"""
    print("CHECKING FRONTEND STATUS")
    print("="*80)
    
    frontend_dir = "c:\\Users\\preio\\perplex-edge\\frontend"
    
    # 1. Check if frontend directory exists
    print("\n1. Checking frontend directory...")
    if os.path.exists(frontend_dir):
        print(f"   OK: Frontend directory exists at {frontend_dir}")
    else:
        print(f"   FAIL: Frontend directory not found")
        return False
    
    # 2. Check package.json
    print("\n2. Checking package.json...")
    package_json = os.path.join(frontend_dir, "package.json")
    if os.path.exists(package_json):
        print("   OK: package.json exists")
        try:
            with open(package_json, "r") as f:
                content = f.read()
                if "react" in content:
                    print("   OK: React project detected")
                if "vite" in content:
                    print("   OK: Vite build tool detected")
        except:
            print("   ERROR: Could not read package.json")
    else:
        print("   FAIL: package.json not found")
        return False
    
    # 3. Check Dockerfile
    print("\n3. Checking Dockerfile...")
    dockerfile = os.path.join(frontend_dir, "Dockerfile")
    if os.path.exists(dockerfile):
        print("   OK: Dockerfile exists")
        try:
            with open(dockerfile, "r") as f:
                content = f.read()
                if "nginx" in content.lower():
                    print("   OK: Nginx configuration found")
        except:
            print("   ERROR: Could not read Dockerfile")
    else:
        print("   FAIL: Dockerfile not found")
        return False
    
    # 4. Check for Railway configuration
    print("\n4. Checking Railway configuration...")
    railway_configs = [
        "c:\\Users\\preio\\perplex-edge\\frontend\\railway.toml",
        "c:\\Users\\preio\\perplex-edge\\frontend\\railway.json",
    ]
    
    railway_found = False
    for config in railway_configs:
        if os.path.exists(config):
            print(f"   OK: Railway config found at {config}")
            railway_found = True
            break
    
    if not railway_found:
        print("   WARNING: No Railway configuration found")
        print("   Frontend may not be configured for Railway deployment")
    
    # 5. Check if frontend is deployed
    print("\n5. Checking frontend deployment...")
    try:
        import requests
        response = requests.get("https://perplex-edge-frontend.up.railway.app/", timeout=5)
        if response.status_code == 200:
            print("   OK: Frontend is deployed and responding")
        else:
            print(f"   FAIL: Frontend returned {response.status_code}")
    except:
        print("   FAIL: Frontend not accessible")
        print("   Possible reasons:")
        print("     - Not deployed to Railway")
        print("     - Wrong URL")
        print("     - Railway service not running")
    
    print("\n" + "="*80)
    return True

if __name__ == "__main__":
    check_frontend()
