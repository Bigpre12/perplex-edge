#!/usr/bin/env python3
"""
Test clean player props endpoints
"""
import requests
import time

def test_clean_props():
    """Test clean player props endpoints"""
    base_url = "https://railway-engine-production.up.railway.app"
    
    print("TESTING CLEAN PLAYER PROPS ENDPOINTS")
    print("="*80)
    
    print("\n1. Clean endpoints deployed!")
    print("   Commit: 1a4a43a")
    print("   Endpoints: /clean/clean-player-props, /clean/super-bowl-props")
    
    print("\n2. Waiting for deployment...")
    time.sleep(30)
    
    print("\n3. Testing Clean NBA Props:")
    try:
        response = requests.get(f"{base_url}/clean/clean-player-props?sport_id=30&limit=5", timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            props = data.get('items', [])
            print(f"   SUCCESS! Found {len(props)} NBA props")
            
            if props:
                print(f"   Sample NBA props:")
                for i, prop in enumerate(props[:3], 1):
                    player = prop.get('player', {})
                    market = prop.get('market', {})
                    print(f"   {i}. {player.get('name', 'N/A')}: {market.get('stat_type', 'N/A')} {prop.get('line_value', 'N/A')}")
                    print(f"      Edge: {prop.get('edge', 0):.2%}")
                    print(f"      Odds: {prop.get('odds', 0)}")
                    print(f"      Confidence: {prop.get('confidence_score', 0):.1f}")
            else:
                print("   No props found - might be empty")
        elif response.status_code == 404:
            print("   404 - Endpoint not found yet, waiting...")
        else:
            print(f"   Error: {response.text[:100]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n4. Testing Super Bowl Props:")
    try:
        response = requests.get(f"{base_url}/clean/super-bowl-props", timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            props = data.get('items', [])
            print(f"   SUCCESS! Found {len(props)} Super Bowl props")
            
            if props:
                print(f"   Super Bowl props:")
                for i, prop in enumerate(props[:5], 1):
                    player = prop.get('player', {})
                    market = prop.get('market', {})
                    print(f"   {i}. {player.get('name', 'N/A')}: {market.get('stat_type', 'N/A')} {prop.get('line_value', 'N/A')}")
                    print(f"      Edge: {prop.get('edge', 0):.2%}")
                    print(f"      Confidence: {prop.get('confidence_score', 0):.1f}")
                    print(f"      Odds: {prop.get('odds', 0)}")
        else:
            print(f"   Error: {response.text[:100]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n5. Testing with different parameters:")
    try:
        response = requests.get(f"{base_url}/clean/clean-player-props?sport_id=31&limit=10", timeout=10)
        print(f"   Clean NFL Props Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            props = data.get('items', [])
            print(f"   Found {len(props)} NFL props")
        else:
            print(f"   Error: {response.text[:100]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n" + "="*80)
    print("CLEAN PROPS STATUS:")
    print("="*80)
    
    print("\nIF CLEAN ENDPOINTS WORK:")
    print("1. Frontend should use: /clean/clean-player-props")
    print("2. Super Bowl props: /clean/super-bowl-props")
    print("3. No CLV columns, no complex joins")
    print("4. Just basic props data")
    
    print("\nIF STILL 404:")
    print("1. Wait 1-2 more minutes")
    print("2. Check if deployment completed")
    print("3. May need to add router to main.py manually")
    
    print("\nTIME CRITICAL:")
    print("Less than 1 hour to Super Bowl!")
    print("These clean endpoints should work immediately!")
    
    print("\n" + "="*80)
    print("PLAYER PROPS: CLEAN VERSION TESTING")
    print("="*80)

if __name__ == "__main__":
    test_clean_props()
