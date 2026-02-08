#!/usr/bin/env python3
"""
Check frontend deployment readiness
"""
import os
import json

def check_deployment_readiness():
    """Check if frontend is ready for deployment"""
    print("CHECKING FRONTEND DEPLOYMENT READINESS")
    print("="*80)
    
    frontend_dir = "c:\\Users\\preio\\perplex-edge\\frontend"
    
    checks = {
        "Railway configuration": False,
        "Dockerfile": False,
        "Nginx configuration": False,
        "Environment variables": False,
        "API proxy configuration": False,
        "Production build ready": False,
    }
    
    # 1. Check Railway configuration
    print("\n1. Railway configuration...")
    railway_toml = os.path.join(frontend_dir, "railway.toml")
    if os.path.exists(railway_toml):
        print("   ✅ railway.toml exists")
        checks["Railway configuration"] = True
    else:
        print("   ❌ railway.toml missing")
    
    # 2. Check Dockerfile
    print("\n2. Dockerfile...")
    dockerfile = os.path.join(frontend_dir, "Dockerfile")
    if os.path.exists(dockerfile):
        print("   ✅ Dockerfile exists")
        checks["Dockerfile"] = True
        
        # Check Dockerfile content
        with open(dockerfile, "r") as f:
            content = f.read()
        
        if "nginx" in content.lower():
            print("   ✅ Uses nginx for production")
            checks["Nginx configuration"] = True
        else:
            print("   ❌ Not using nginx")
        
        if "VITE_API_BASE_URL" in content:
            print("   ✅ API URL configured")
            checks["API proxy configuration"] = True
        else:
            print("   ❌ API URL not configured")
    else:
        print("   ❌ Dockerfile missing")
    
    # 3. Check environment variables
    print("\n3. Environment variables...")
    env_prod = os.path.join(frontend_dir, ".env.production")
    if os.path.exists(env_prod):
        with open(env_prod, "r") as f:
            content = f.read()
        
        if "VITE_API_BASE_URL" in content:
            print("   ✅ .env.production has VITE_API_BASE_URL")
            checks["Environment variables"] = True
        else:
            print("   ❌ VITE_API_BASE_URL not in .env.production")
    else:
        print("   ❌ .env.production missing")
    
    # 4. Check package.json
    print("\n4. Package.json...")
    package_json = os.path.join(frontend_dir, "package.json")
    if os.path.exists(package_json):
        with open(package_json, "r") as f:
            data = json.load(f)
        
        if "build" in data.get("scripts", {}):
            print("   ✅ Build script exists")
            checks["Production build ready"] = True
        else:
            print("   ❌ Build script missing")
    else:
        print("   ❌ package.json missing")
    
    # 5. Check nginx.conf
    print("\n5. Nginx configuration...")
    nginx_conf = os.path.join(frontend_dir, "nginx.conf")
    if os.path.exists(nginx_conf):
        with open(nginx_conf, "r") as f:
            content = f.read()
        
        if "proxy_pass" in content:
            print("   ✅ API proxy configured")
        else:
            print("   ❌ API proxy not configured")
    else:
        print("   ❌ nginx.conf missing")
    
    print("\n" + "="*80)
    
    # Summary
    passed = sum(checks.values())
    total = len(checks)
    
    print(f"DEPLOYMENT READINESS: {passed}/{total} checks passed")
    
    if passed == total:
        print("✅ FRONTEND IS READY FOR DEPLOYMENT!")
    else:
        print("⚠️  FRONTEND NEEDS ATTENTION:")
        for check, status in checks.items():
            if not status:
                print(f"   ❌ {check}")
    
    print("="*80)
    
    return passed == total

if __name__ == "__main__":
    check_deployment_readiness()
<arg_value>EmptyFile</arg_key>
<arg_value>false
