#!/usr/bin/env python3
"""
QUICK TEST - Check if any endpoints are working
"""
import requests

def quick_test():
    """Quick test of endpoints"""
    base_url = "https://railway-engine-production.up.railway.app"
    
    print("QUICK TEST - CHECKING ENDPOINTS")
    print("="*80)
    
    # Test basic endpoints
    endpoints = [
        ("Health", "/api/health"),
        ("Admin SQL", "/admin/sql"),
        ("Immediate Props", "/immediate/working-player-props"),
        ("Immediate Parlays", "/immediate/working-parlays")
    ]
    
    for name, endpoint in endpoints:
        try:
            if name == "Admin SQL":
                # Skip SQL endpoint for now
                continue
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            print(f"{name}: {response.status_code}")
        except Exception as e:
            print(f"{name}: ERROR - {e}")
    
    print("\n" + "="*80)
    print("QUICK TEST COMPLETE")
    print("="*80)

if __name__ == "__main__":
    quick_test()
