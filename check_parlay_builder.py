#!/usr/bin/env python3
"""
Check ParlayBuilder for issues
"""
import os
import re

def check_parlay_builder():
    """Check ParlayBuilder component for issues"""
    print("CHECKING PARLAYBUILDER ISSUES")
    print("="*80)
    
    frontend_dir = "c:\\Users\\preio\\perplex-edge\\frontend"
    backend_dir = "c:\\Users\\preio\\perplex-edge\\backend"
    
    issues = []
    
    # 1. Check frontend ParlayBuilder
    print("\n1. Checking frontend ParlayBuilder...")
    parlay_file = os.path.join(frontend_dir, "src\\components\\ParlayBuilder.tsx")
    if os.path.exists(parlay_file):
        with open(parlay_file, "r", encoding='utf-8') as f:
            content = f.read()
        
        # Check for API calls
        api_calls = [
            "useParlayBuilder",
            "fetchAutoGenerateSlips",
            "createSharedCard",
            "quoteParlayLegs",
        ]
        
        for call in api_calls:
            if call in content:
                print(f"   OK: Found {call}")
            else:
                issues.append(f"Missing {call} in ParlayBuilder")
                print(f"   WARNING: Missing {call}")
        
        # Check for error handling
        if "try {" in content and "catch" in content:
            print("   OK: Error handling present")
        else:
            issues.append("No error handling in ParlayBuilder")
            print("   WARNING: No error handling")
        
        # Check for loading states
        if "isLoading" in content:
            print("   OK: Loading states handled")
        else:
            issues.append("No loading states in ParlayBuilder")
            print("   WARNING: No loading states")
    else:
        issues.append("ParlayBuilder.tsx not found")
        print("   ERROR: ParlayBuilder.tsx not found")
    
    # 2. Check backend parlay endpoints
    print("\n2. Checking backend parlay endpoints...")
    public_api = os.path.join(backend_dir, "app\\api\\public.py")
    if os.path.exists(public_api):
        with open(public_api, "r", encoding='utf-8') as f:
            content = f.read()
        
        endpoints = [
            "/sports/{sport_id}/parlays/builder",
            "/sports/{sport_id}/parlays/auto-generate",
            "/parlays/create-shared-card",
            "/parlays/quote",
            "/parlays/odds-health",
        ]
        
        for endpoint in endpoints:
            if endpoint.replace("{sport_id}", "\\d+") in content:
                print(f"   OK: Found {endpoint}")
            else:
                issues.append(f"Missing endpoint {endpoint}")
                print(f"   WARNING: Missing endpoint {endpoint}")
    else:
        issues.append("public.py not found")
        print("   ERROR: public.py not found")
    
    # 3. Check for CORS issues
    print("\n3. Checking CORS configuration...")
    main_py = os.path.join(backend_dir, "app\\main.py")
    if os.path.exists(main_py):
        with open(main_py, "r", encoding='utf-8') as f:
            content = f.read()
        
        if "CORSMiddleware" in content:
            print("   OK: CORS configured")
        else:
            issues.append("CORS not configured")
            print("   WARNING: CORS not configured")
    
    # 4. Check rate limiting
    print("\n4. Checking rate limiting...")
    if "parlays_rate_limit" in content:
        print("   OK: Rate limiting configured for parlays")
    else:
        issues.append("No rate limiting for parlays")
        print("   WARNING: No rate limiting for parlays")
    
    # 5. Check database queries
    print("\n5. Checking database queries...")
    if ".limit(" in content and "parlay" in content.lower():
        print("   OK: Parlay queries have limits")
    else:
        issues.append("Parlay queries may be unlimited")
        print("   WARNING: Parlay queries may be unlimited")
    
    print("\n" + "="*80)
    
    if issues:
        print(f"FOUND {len(issues)} ISSUES:")
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")
    else:
        print("SUCCESS: No issues found!")
    
    print("="*80)
    
    return issues

if __name__ == "__main__":
    check_parlay_builder()
