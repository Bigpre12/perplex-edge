#!/usr/bin/env python3
"""
Check sportsbook intelligence for Super Bowl predictions
"""
import requests

def check_sportsbook_intelligence():
    """Check sportsbook intelligence"""
    base_url = "https://railway-engine-production.up.railway.app"
    
    print("CHECKING SPORTSBOOK INTELLIGENCE")
    print("="*80)
    
    # Check sportsbook intelligence endpoint
    print("\n1. Sportsbook Intelligence Endpoint:")
    intel_url = f"{base_url}/api/sportsbook_intelligence/intelligence"
    
    try:
        response = requests.get(intel_url, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Data keys: {list(data.keys())[:5]}")
            
            # Look for Super Bowl related data
            if 'super_bowl' in str(data).lower() or 'seahawks' in str(data).lower() or 'patriots' in str(data).lower():
                print("   Super Bowl data found!")
                print(f"   Sample: {data}")
            else:
                print("   No Super Bowl data in response")
        else:
            print(f"   Error: {response.text[:100]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Check trading signals
    print("\n2. Trading Signals:")
    signals_url = f"{base_url}/api/sportsbook_intelligence/signals"
    
    try:
        response = requests.get(signals_url, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            signals = data.get('signals', [])
            print(f"   Found {len(signals)} trading signals")
            
            # Look for Super Bowl related signals
            sb_signals = [s for s in signals if 'super_bowl' in str(s).lower() or 'seahawks' in str(s).lower() or 'patriots' in str(s).lower()]
            if sb_signals:
                print(f"   Super Bowl signals: {len(sb_signals)}")
                for signal in sb_signals[:3]:
                    print(f"     - {signal}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n" + "="*80)
    print("SUPER BOWL LX MATCHUP SUMMARY:")
    print("- Seahawks vs Patriots")
    print("- Time: 5:30 PM CT (11:30 PM ET)")
    print("- Location: Levi's Stadium, Santa Clara, CA")
    print("- Seahawks favored by 3 points")
    print("- Both teams 14-3 records")
    print("- Explosive plays battle: Seahawks defense vs Patriots offense")
    print("="*80)

if __name__ == "__main__":
    check_sportsbook_intelligence()
