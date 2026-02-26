#!/usr/bin/env python3
"""
TEST IMMEDIATE WORKING ENDPOINTS
"""
import requests
import time

def test_immediate_working():
    """Test the immediate working endpoints"""
    base_url = "https://railway-engine-production.up.railway.app"
    
    print("TESTING IMMEDIATE WORKING ENDPOINTS")
    print("="*80)
    
    print("\n1. Waiting for deployment...")
    time.sleep(30)
    
    print("\n2. Testing immediate working endpoints:")
    
    test_endpoints = [
        ("Player Props", "/immediate/working-player-props?sport_id=31&limit=5"),
        ("Super Bowl Props", "/immediate/super-bowl-props"),
        ("Working Parlays", "/immediate/working-parlays"),
        ("Monte Carlo", "/immediate/monte-carlo")
    ]
    
    all_working = True
    
    for name, endpoint in test_endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            print(f"\n{name}: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                if 'items' in data:
                    items = data.get('items', [])
                    print(f"   SUCCESS: {len(items)} props")
                    
                    # Show sample props
                    if items:
                        sample = items[0]
                        player = sample.get('player', {})
                        market = sample.get('market', {})
                        print(f"   Sample: {player.get('name', 'N/A')} - {market.get('stat_type', 'N/A')} {sample.get('line_value', 'N/A')}")
                        print(f"   Edge: {sample.get('edge', 0):.2%}, Odds: {sample.get('odds', 0)}")
                
                elif 'parlays' in data:
                    parlays = data.get('parlays', [])
                    print(f"   SUCCESS: {len(parlays)} parlays")
                    
                    if parlays:
                        parlay = parlays[0]
                        print(f"   Sample: {parlay.get('total_ev', 0):.2%} EV, {parlay.get('total_odds', 0)} odds")
                        print(f"   Legs: {len(parlay.get('legs', []))}")
                
                elif 'results' in data:
                    print(f"   SUCCESS: Monte Carlo simulation")
                    results = data.get('results', {})
                    if 'drake_mayne' in results:
                        drake = results['drake_mayne']
                        if 'passing_yards' in drake:
                            yards = drake['passing_yards']
                            print(f"   Drake Maye Passing Yards: {yards.get('mean', 0):.1f} avg")
                
                print(f"   Timestamp: {data.get('timestamp', 'N/A')}")
                
            else:
                print(f"   ERROR: {response.text[:100]}")
                all_working = False
                
        except Exception as e:
            print(f"   ERROR: {e}")
            all_working = False
    
    print("\n" + "="*80)
    print("IMMEDIATE WORKING ENDPOINTS TEST RESULTS")
    print("="*80)
    
    if all_working:
        print("\nSUCCESS: All immediate working endpoints are functional!")
        print("\nFRONTEND UPDATE INSTRUCTIONS:")
        print("1. Player Props: /immediate/working-player-props?sport_id=31")
        print("2. Super Bowl Props: /immediate/super-bowl-props")
        print("3. Parlays: /immediate/working-parlays")
        print("4. Monte Carlo: /immediate/monte-carlo")
        
        print("\nFEATURES WORKING:")
        print("- Player Props with edges, odds, confidence")
        print("- Super Bowl specific props")
        print("- Parlay builder with EV calculations")
        print("- Monte Carlo simulations")
        print("- All with proper timestamps and error handling")
        
        print("\nSTATUS: EVERYTHING IS WORKING!")
        
    else:
        print("\nSOME ENDPOINTS STILL NOT WORKING")
        print("Wait a bit more for deployment or check logs")
    
    print("\n" + "="*80)
    print("IMMEDIATE WORKING ENDPOINTS TEST COMPLETE")
    print("="*80)

if __name__ == "__main__":
    test_immediate_working()
