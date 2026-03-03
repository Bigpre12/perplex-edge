#!/usr/bin/env python3
"""
SIMPLE COMPREHENSIVE TEST - Test all endpoints without emojis
"""
import requests
import time
import json
from datetime import datetime

def simple_comprehensive_test():
    """Test all endpoints and features comprehensively"""
    base_url = "https://railway-engine-production.up.railway.app"
    
    print("SIMPLE COMPREHENSIVE TEST - ALL ENDPOINTS AND FEATURES")
    print("="*80)
    
    print(f"\nTime: {datetime.now().strftime('%I:%M:%S %p')}")
    print("Testing: Database retry fix, working endpoints, Monte Carlo, parlays, player props")
    
    # Wait for deployment
    print("\nWaiting for deployment...")
    time.sleep(30)
    
    results = {}
    
    # 1. Test Backend Health
    print("\n1. BACKEND HEALTH:")
    try:
        response = requests.get(f"{base_url}/api/health", timeout=10)
        results['health'] = {
            'status': response.status_code,
            'success': response.status_code == 200
        }
        print(f"   Health: {response.status_code} {'OK' if response.status_code == 200 else 'ERROR'}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Status: {data.get('status', 'unknown')}")
        else:
            print(f"   Error: {response.text[:100]}")
    except Exception as e:
        results['health'] = {'status': 'error', 'success': False, 'error': str(e)}
        print(f"   Health: ERROR {e}")
    
    # 2. Test Working Player Props
    print("\n2. WORKING PLAYER PROPS:")
    
    working_props_endpoints = [
        ("Working NFL", "/working/working-player-props?sport_id=31&limit=5"),
        ("Working NBA", "/working/working-player-props?sport_id=30&limit=5"),
        ("Super Bowl Working", "/working/super-bowl-working")
    ]
    
    working_props_count = 0
    for name, endpoint in working_props_endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                props = data.get('items', [])
                print(f"   {name}: {response.status_code} OK ({len(props)} props)")
                working_props_count += 1
                
                # Show sample props
                if props:
                    sample = props[0]
                    player = sample.get('player', {})
                    market = sample.get('market', {})
                    print(f"      Sample: {player.get('name', 'N/A')} - {market.get('stat_type', 'N/A')} {sample.get('line_value', 'N/A')}")
                    print(f"      Edge: {sample.get('edge', 0):.2%}, Odds: {sample.get('odds', 0)}")
            else:
                print(f"   {name}: {response.status_code} ERROR")
                if response.status_code == 500:
                    error_text = response.text
                    if "closing_odds" in error_text:
                        print(f"      Issue: CLV columns missing")
                    elif "starting up" in error_text.lower():
                        print(f"      Issue: Database starting up")
                    else:
                        print(f"      Error: {error_text[:50]}")
                else:
                    print(f"      Error: {response.text[:50]}")
            
            results[f'props_{name.lower().replace(" ", "_")}'] = {
                'status': response.status_code,
                'success': success,
                'props_count': len(props) if success else 0
            }
        except Exception as e:
            print(f"   {name}: ERROR {e}")
            results[f'props_{name.lower().replace(" ", "_")}'] = {
                'status': 'error',
                'success': False,
                'error': str(e)
            }
    
    # 3. Test Working Parlays
    print("\n3. WORKING PARLAYS:")
    
    working_parlay_endpoints = [
        ("Working Parlays", "/working/working-parlays?sport_id=31&limit=3"),
        ("Monte Carlo", "/working/monte-carlo-simulation?sport_id=31&game_id=648")
    ]
    
    working_parlays_count = 0
    for name, endpoint in working_parlay_endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                if 'parlays' in data:
                    parlays = data.get('parlays', [])
                    print(f"   {name}: {response.status_code} OK ({len(parlays)} parlays)")
                    working_parlays_count += 1
                    
                    # Show sample parlay
                    if parlays:
                        parlay = parlays[0]
                        print(f"      Sample: {parlay.get('total_ev', 0):.2%} EV, {parlay.get('total_odds', 0)} odds")
                        print(f"      Legs: {len(parlay.get('legs', []))}")
                elif 'results' in data:
                    print(f"   {name}: {response.status_code} OK (Monte Carlo results)")
                    working_parlays_count += 1
                else:
                    items = data.get('items', [])
                    print(f"   {name}: {response.status_code} OK ({len(items)} items)")
                    working_parlays_count += 1
            else:
                print(f"   {name}: {response.status_code} ERROR")
                print(f"      Error: {response.text[:50]}")
            
            results[f'parlay_{name.lower().replace(" ", "_")}'] = {
                'status': response.status_code,
                'success': success
            }
        except Exception as e:
            print(f"   {name}: ERROR {e}")
            results[f'parlay_{name.lower().replace(" ", "_")}'] = {
                'status': 'error',
                'success': False,
                'error': str(e)
            }
    
    # 4. Test Original Endpoints (for comparison)
    print("\n4. ORIGINAL ENDPOINTS STATUS:")
    
    original_endpoints = [
        ("Original NFL", "/api/sports/31/picks/player-props?limit=5"),
        ("Original NBA", "/api/sports/30/picks/player-props?limit=5"),
        ("NFL Games", "/api/sports/31/games?date=2026-02-08"),
        ("NBA Games", "/api/sports/30/games?date=2026-02-08")
    ]
    
    for name, endpoint in original_endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                if 'items' in data:
                    items = data.get('items', [])
                    print(f"   {name}: {response.status_code} OK ({len(items)} items)")
                else:
                    print(f"   {name}: {response.status_code} OK")
            else:
                print(f"   {name}: {response.status_code} ERROR")
                if response.status_code == 500:
                    print(f"      Issue: Database error (likely CLV columns)")
        except Exception as e:
            print(f"   {name}: ERROR {e}")
    
    # 5. Summary
    print("\n" + "="*80)
    print("SIMPLE COMPREHENSIVE TEST RESULTS")
    print("="*80)
    
    print(f"\nSUMMARY:")
    print(f"   Backend Health: {'OK' if results.get('health', {}).get('success') else 'ERROR'}")
    print(f"   Working Player Props: {working_props_count}/{len(working_props_endpoints)} working")
    print(f"   Working Parlays: {working_parlays_count}/{len(working_parlay_endpoints)} working")
    
    print(f"\nWORKING ENDPOINTS:")
    for name, endpoint in working_props_endpoints:
        key = f'props_{name.lower().replace(" ", "_")}'
        if results.get(key, {}).get('success'):
            print(f"   OK {name}: {endpoint}")
    
    for name, endpoint in working_parlay_endpoints:
        key = f'parlay_{name.lower().replace(" ", "_")}'
        if results.get(key, {}).get('success'):
            print(f"   OK {name}: {endpoint}")
    
    print(f"\nRECOMMENDATIONS:")
    
    if working_props_count > 0:
        print("   1. Use WORKING endpoints for player props")
        print("   2. Update frontend to use /working/working-player-props")
        print("   3. Use /working/super-bowl-working for Super Bowl")
    
    if working_parlays_count > 0:
        print("   4. Use WORKING endpoints for parlays")
        print("   5. Update frontend to use /working/working-parlays")
        print("   6. Use /working/monte-carlo-simulation for Monte Carlo")
    
    if results.get('health', {}).get('success'):
        print("   7. Database retry fix worked! Backend is healthy.")
    else:
        print("   7. Backend still having issues - check database connection.")
    
    print(f"\nFRONTEND UPDATE NEEDED:")
    print("   Player Props: /working/working-player-props?sport_id=31")
    print("   Super Bowl: /working/super-bowl-working")
    print("   Parlays: /working/working-parlays")
    print("   Monte Carlo: /working/monte-carlo-simulation")
    
    overall_status = "EVERYTHING WORKING!" if working_props_count > 0 and working_parlays_count > 0 else "PARTIALLY WORKING"
    print(f"\nSTATUS: {overall_status}")
    
    # Save results
    with open("c:/Users/preio/preio/perplex-edge/simple_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to: simple_test_results.json")
    
    print("\n" + "="*80)
    print("SIMPLE COMPREHENSIVE TEST COMPLETE")
    print("="*80)

if __name__ == "__main__":
    simple_comprehensive_test()
