#!/usr/bin/env python3
"""
Monitor Railway frontend deployment
"""
import subprocess
import time
import requests

def monitor_deployment():
    """Monitor Railway deployment"""
    print("MONITORING RAILWAY FRONTEND DEPLOYMENT")
    print("="*80)
    
    max_attempts = 30
    attempt = 0
    
    while attempt < max_attempts:
        attempt += 1
        print(f"\nAttempt {attempt}/{max_attempts}")
        
        try:
            # Check deployment status
            result = subprocess.run(
                ["powershell", "-ExecutionPolicy", "Bypass", "-Command", "railway status"],
                capture_output=True,
                text=True,
                cwd="c:\\Users\\preio\\perplex-edge\\frontend"
            )
            
            print("Railway Status:")
            print(result.stdout)
            
            # Try to get the URL
            if "Service:" in result.stdout and "None" not in result.stdout:
                print("\n✅ Deployment appears to be ready!")
                
                # Try to access the frontend
                try:
                    response = requests.get("https://perplex-edge-frontend.up.railway.app/", timeout=5)
                    if response.status_code == 200:
                        print(f"✅ Frontend is accessible! Status: {response.status_code}")
                        break
                except:
                    print("⏳ Frontend not accessible yet, still deploying...")
            
        except Exception as e:
            print(f"Error checking status: {e}")
        
        if attempt < max_attempts:
            print("Waiting 10 seconds before next check...")
            time.sleep(10)
    
    print("\n" + "="*80)
    print("Deployment monitoring complete!")
    print("="*80)

if __name__ == "__main__":
    monitor_deployment()
