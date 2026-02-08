#!/usr/bin/env python3
"""
Deploy frontend to Railway
"""
import subprocess
import sys
import os

def deploy_frontend():
    """Deploy frontend to Railway"""
    print("DEPLOYING FRONTEND TO RAILWAY")
    print("="*80)
    
    # Check if Railway CLI is installed
    print("\n1. Checking Railway CLI...")
    try:
        result = subprocess.run(["railway", "--version"], capture_output=True, text=True)
        print(f"   OK: Railway CLI found - {result.stdout.strip()}")
    except:
        print("   FAIL: Railway CLI not found")
        print("   Please install Railway CLI: npm install -g @railway/cli")
        return False
    
    # Change to frontend directory
    frontend_dir = "c:\\Users\\preio\\perplex-edge\\frontend"
    os.chdir(frontend_dir)
    print(f"\n2. Changed to frontend directory: {frontend_dir}")
    
    # Check if logged in
    print("\n3. Checking Railway login...")
    try:
        result = subprocess.run(["railway", "status"], capture_output=True, text=True)
        if "Not logged in" in result.stdout:
            print("   FAIL: Not logged in to Railway")
            print("   Please run: railway login")
            return False
        else:
            print("   OK: Logged in to Railway")
    except:
        print("   ERROR: Could not check Railway status")
        return False
    
    # Link project if not already linked
    print("\n4. Checking project link...")
    if not os.path.exists(".railway"):
        print("   Linking to Railway project...")
        try:
            subprocess.run(["railway", "link"], check=True)
            print("   OK: Project linked")
        except:
            print("   ERROR: Failed to link project")
            return False
    else:
        print("   OK: Project already linked")
    
    # Deploy
    print("\n5. Deploying frontend...")
    try:
        subprocess.run(["railway", "up"], check=True)
        print("   OK: Deployment started")
    except:
        print("   ERROR: Failed to deploy")
        return False
    
    print("\n" + "="*80)
    print("Frontend deployment initiated!")
    print("Monitor deployment at: https://railway.app")
    print("="*80)
    
    return True

if __name__ == "__main__":
    deploy_frontend()
