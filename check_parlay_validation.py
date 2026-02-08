#!/usr/bin/env python3
"""
Check parlay builder validation
"""
import requests
import json

def check_parlay_validation():
    """Check parlay builder validation"""
    base_url = "https://railway-engine-production.up.railway.app"
    
    print("CHECKING PARLAY BUILDER VALIDATION")
    print("="*80)
    
    # Try with different parameters
    test_cases = [
        ("leg_count=2", "2 legs"),
        ("leg_count=3&max_results=1", "3 legs, 1 result"),
        ("leg_count=3&min_leg_grade=F", "3 legs, grade F"),
        ("leg_count=3&include_100_pct=false", "3 legs, no 100%"),
        ("leg_count=3&block_correlated=false", "3 legs, allow correlated"),
    ]
    
    for params, desc in test_cases:
        url = f"{base_url}/api/sports/30/parlays/builder?{params}"
        print(f"\n{desc}: {params}")
        
        try:
            response = requests.get(url, timeout=10)
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"  Success: {len(data.get('parlays', []))} parlays")
            else:
                error_text = response.text
                if "validation error" in error_text:
                    # Extract the validation error details
                    try:
                        error_data = response.json()
                        print(f"  Validation Error: {error_data.get('error', 'Unknown')}")
                        if 'model_status' in error_text:
                            print("  Issue: model_status field missing")
                    except:
                        pass
                else:
                    print(f"  Error: {error_text[:100]}")
        except Exception as e:
            print(f"  Error: {e}")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    check_parlay_validation()
