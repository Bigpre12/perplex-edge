#!/usr/bin/env python3
"""
Continuous loop to monitor and fix frontend and backend issues
"""
import subprocess
import time
import requests
from datetime import datetime

def check_backend():
    """Check backend health"""
    try:
        response = requests.get("https://railway-engine-production.up.railway.app/health", timeout=5)
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, f"HTTP {response.status_code}"
    except Exception as e:
        return False, str(e)

def check_frontend():
    """Check frontend health"""
    try:
        response = requests.get("https://perplex-edge-frontend.up.railway.app/", timeout=5)
        if response.status_code == 200:
            return True, "Frontend is responding"
        else:
            return False, f"HTTP {response.status_code}"
    except Exception as e:
        return False, str(e)

def check_api_endpoint():
    """Check if API is accessible"""
    try:
        response = requests.get("https://railway-engine-production.up.railway.app/api/grading/health", timeout=5)
        if response.status_code == 200:
            return True, "API endpoint working"
        else:
            return False, f"HTTP {response.status_code}"
    except Exception as e:
        return False, str(e)

def run_syntax_check():
    """Run syntax check on all files"""
    try:
        result = subprocess.run(
            ["python", "check_syntax_errors.py"],
            capture_output=True,
            text=True,
            cwd="c:\\Users\\preio\\perplex-edge"
        )
        if result.returncode == 0:
            return True, "No syntax errors"
        else:
            return False, result.stderr
    except Exception as e:
        return False, str(e)

def main():
    """Main monitoring loop"""
    print("CONTINUOUS MONITORING AND FIXING LOOP")
    print("="*80)
    print("Press Ctrl+C to stop")
    print("="*80)
    
    iteration = 0
    
    while True:
        iteration += 1
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"\n[{timestamp}] Iteration {iteration}")
        print("-" * 40)
        
        # Check 1: Backend health
        backend_ok, backend_msg = check_backend()
        print(f"Backend: {'OK' if backend_ok else 'FAIL'} {backend_msg}")
        
        # Check 2: Frontend health
        frontend_ok, frontend_msg = check_frontend()
        print(f"Frontend: {'OK' if frontend_ok else 'FAIL'} {frontend_msg}")
        
        # Check 3: API endpoint
        api_ok, api_msg = check_api_endpoint()
        print(f"API: {'OK' if api_ok else 'FAIL'} {api_msg}")
        
        # Check 4: Syntax errors
        syntax_ok, syntax_msg = run_syntax_check()
        print(f"Syntax: {'OK' if syntax_ok else 'FAIL'} {syntax_msg}")
        
        # Overall status
        all_ok = backend_ok and frontend_ok and api_ok and syntax_ok
        
        if all_ok:
            print("\nSUCCESS! ALL SYSTEMS OPERATIONAL!")
            print("Backend, Frontend, API, and Syntax are all working correctly.")
            break
        else:
            print(f"\nWARNING: Issues detected. Waiting 30 seconds before next check...")
            time.sleep(30)
    
    print("\n" + "="*80)
    print("MONITORING COMPLETE - ALL ISSUES RESOLVED")
    print("="*80)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user")
    except Exception as e:
        print(f"\nError in monitoring loop: {e}")
