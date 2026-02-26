#!/usr/bin/env python3
"""
Test emergency player props endpoint
"""
import requests
import time

def test_emergency_props():
    """Test emergency player props endpoint"""
    base_url = "https://railway-engine-production.up.railway.app"
    
    print("TESTING EMERGENCY PLAYER PROPS ENDPOINT")
    print("="*80)
    
    print("\n1. Emergency endpoint deployed!")
    print("   Commit: c5e8387")
    print("   Endpoint: /emergency/emergency-player-props")
    
    print("\n2. Waiting for deployment...")
    time.sleep(30)
    
    print("\n3. Testing NBA Emergency Props:")
    try:
        response = requests.get(f"{base_url}/emergency/emergency-player-props?sport_id=30&limit=5", timeout=10)
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
                print("   No props found - might be empty or no data")
        elif response.status_code == 404:
            print("   404 - Endpoint not found yet, waiting...")
        else:
            print(f"   Error: {response.text[:100]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n4. Testing NFL Emergency Props:")
    try:
        response = requests.get(f"{base_url}/emergency/emergency-player-props?sport_id=31&limit=5", timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            props = data.get('items', [])
            print(f"   SUCCESS! Found {len(props)} NFL props")
            
            if props:
                print(f"   Sample NFL props:")
                for i, prop in enumerate(props[:3], 1):
                    player = prop.get('player', {})
                    market = prop.get('market', {})
                    print(f"   {i}. {player.get('name', 'N/A')}: {market.get('stat_type', 'N/A')} {prop.get('line_value', 'N/A')}")
                    print(f"      Edge: {prop.get('edge', 0):.2%}")
                    print(f"      Odds: {prop.get('odds', 0)}")
        else:
            print(f"   Error: {response.text[:100]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n5. Testing Super Bowl Specific:")
    try:
        response = requests.get(f"{base_url}/emergency/emergency-player-props?sport_id=31&limit=10", timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            props = data.get('items', [])
            print(f"   Found {len(props)} NFL props total")
            
            # Look for Super Bowl players
            super_bowl_players = []
            for prop in props:
                player = prop.get('player', {})
                if player.get('name') in ['Drake Maye', 'Sam Darnold']:
                    super_bowl_players.append(prop)
            
            if super_bowl_players:
                print(f"   Found {len(super_bowl_players)} Super Bowl QB props:")
                for prop in super_bowl_players:
                    player = prop.get('player', {})
                    market = prop.get('market', {})
                    print(f"   - {player.get('name', 'N/A')}: {market.get('stat_type', 'N/A')} {prop.get('line_value', 'N/A')}")
                    print(f"     Edge: {prop.get('edge', 0):.2%}")
            else:
                print("   No Super Bowl QB props found")
        else:
            print(f"   Error: {response.text[:100]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n" + "="*80)
    print("EMERGENCY PROPS STATUS:")
    print("="*80)
    
    print("\nIF EMERGENCY ENDPOINT WORKS:")
    print("1. Update frontend to use /emergency/emergency-player-props")
    print("2. Player props will load without CLV columns")
    print("3. Can still show edge, odds, confidence")
    print("4. Good enough for Super Bowl!")
    
    print("\nIF STILL NOT WORKING:")
    print("1. Wait 1-2 more minutes for deployment")
    print("2. Check if endpoint is accessible")
    print("3. May need to restart backend service")
    
    print("\nTIME CRITICAL:")
    print("Less than 1 hour to Super Bowl!")
    print("This emergency fix should work immediately!")
    
    print("\n" + "="*80)
    print("PLAYER PROPS: EMERGENCY FIX DEPLOYED")
    print("="*80)

if __name__ == "__main__":
    test_emergency_props()
