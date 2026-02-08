#!/usr/bin/env python3
"""
Test sportsbook intelligence endpoints
"""
import requests

def test_sportsbook_intelligence():
    """Test sportsbook intelligence endpoints"""
    base_url = "https://railway-engine-production.up.railway.app"
    
    print("TESTING SPORTSBOOK INTELLIGENCE")
    print("="*80)
    
    endpoints = [
        ("/api/api/sportsbook/intelligence", "Sportsbook Intelligence"),
        ("/api/api/sportsbook/market-analysis?sport_id=30", "NBA Market Analysis"),
        ("/api/api/sportsbook/market-summary", "Market Summary"),
        ("/api/api/sportsbook/trading-signals", "Trading Signals"),
    ]
    
    for endpoint, desc in endpoints:
        url = base_url + endpoint
        print(f"\n{desc}: {endpoint}")
        
        try:
            response = requests.get(url, timeout=10)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Keys: {list(data.keys())[:5]}")
                
                # Look for Super Bowl or Seahawks/Patriots data
                content_str = str(data)
                if any(keyword in content_str.lower() for keyword in ['super_bowl', 'seahawks', 'patriots']):
                    print("   Super Bowl related data found!")
                else:
                    print("   No Super Bowl data in response")
            else:
                print(f"   Error: {response.text[:100]}")
        except Exception as e:
            print(f"   Error: {e}")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    test_sportsbook_intelligence()
