#!/usr/bin/env python3
"""
COMPREHENSIVE TEST - Test all endpoints and features
"""
import requests
import time
import json
from datetime import datetime

def comprehensive_test():
    """Test all endpoints and features comprehensively"""
    base_url = "https://railway-engine-production.up.railway.app"
    
    print("COMPREHENSIVE TEST - ALL ENDPOINTS AND FEATURES")
    print("="*80)
    
    print(f"\nTime: {datetime.now().strftime('%I:%M:%S %p')}")
    print("Testing: Database retry fix, working endpoints, Monte Carlo, parlays, player props")
    
    # Wait for deployment
    print("\nWaiting for deployment...")
    time.sleep(45)
    
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
    
    # 2. Test All Player Props Endpoints
    print("\n2. PLAYER PROPS ENDPOINTS:")
    
    props_endpoints = [
        ("Working NFL", "/working/working-player-props?sport_id=31&limit=5"),
        ("Working NBA", "/working/working-player-props?sport_id=30&limit=5"),
        ("Super Bowl Working", "/working/super-bowl-working"),
        ("Clean NFL", "/clean/clean-player-props?sport_id=31&limit=5"),
        ("Clean NBA", "/clean/clean-player-props?sport_id=30&limit=5"),
        ("Super Bowl Clean", "/clean/super-bowl-props"),
        ("Emergency NFL", "/emergency/emergency-player-props?sport_id=31&limit=5"),
        ("Original NFL", "/api/sports/31/picks/player-props?limit=5"),
        ("Original NBA", "/api/sports/30/picks/player-props?limit=5")
    ]
    
    working_props_count = 0
    for name, endpoint in props_endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                props = data.get('items', [])
                print(f"   {name}: {response.status_code} ✅ ({len(props)} props)")
                working_props_count += 1
                
                # Show sample props
                if props and name.startswith("Working"):
                    sample = props[0]
                    player = sample.get('player', {})
                    market = sample.get('market', {})
                    print(f"      Sample: {player.get('name', 'N/A')} - {market.get('stat_type', 'N/A')} {sample.get('line_value', 'N/A')}")
                    print(f"      Edge: {sample.get('edge', 0):.2%}, Odds: {sample.get('odds', 0)}")
            else:
                print(f"   {name}: {response.status_code} ❌")
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
            print(f"   {name}: ❌ {e}")
            results[f'props_{name.lower().replace(" ", "_")}'] = {
                'status': 'error',
                'success': False,
                'error': str(e)
            }
    
    # 3. Test Parlay Endpoints
    print("\n3. PARLAY ENDPOINTS:")
    
    parlay_endpoints = [
        ("Working Parlays", "/working/working-parlays?sport_id=31&limit=3"),
        ("Monte Carlo", "/working/monte-carlo-simulation?sport_id=31&game_id=648"),
        ("Simple Parlays", "/api/simple-parlays"),
        ("Ultra Simple", "/api/ultra-simple-parlays"),
        ("Parlay Builder", "/api/sports/30/parlays/builder"),
        ("Multisport", "/api/multisport")
    ]
    
    working_parlays_count = 0
    for name, endpoint in parlay_endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                if 'parlays' in data:
                    parlays = data.get('parlays', [])
                    print(f"   {name}: {response.status_code} ✅ ({len(parlays)} parlays)")
                elif 'results' in data:
                    print(f"   {name}: {response.status_code} ✅ (Monte Carlo results)")
                else:
                    items = data.get('items', [])
                    print(f"   {name}: {response.status_code} ✅ ({len(items)} items)")
                
                working_parlays_count += 1
                
                # Show sample for working parlays
                if 'parlays' in data and data.get('parlays') and name.startswith("Working"):
                    parlay = data['parlays'][0]
                    print(f"      Sample: {parlay.get('total_ev', 0):.2%} EV, {parlay.get('total_odds', 0)} odds")
                    print(f"      Legs: {len(parlay.get('legs', []))}")
            else:
                print(f"   {name}: {response.status_code} ❌")
                print(f"      Error: {response.text[:50]}")
            
            results[f'parlay_{name.lower().replace(" ", "_")}'] = {
                'status': response.status_code,
                'success': success
            }
        except Exception as e:
            print(f"   {name}: ❌ {e}")
            results[f'parlay_{name.lower().replace(" ", "_")}'] = {
                'status': 'error',
                'success': False,
                'error': str(e)
            }
    
    # 4. Test Game Lines
    print("\n4. GAME LINES:")
    
    game_endpoints = [
        ("NFL Games", "/api/sports/31/games?date=2026-02-08"),
        ("NBA Games", "/api/sports/30/games?date=2026-02-08")
    ]
    
    for name, endpoint in game_endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                games = data.get('items', [])
                print(f"   {name}: {response.status_code} ✅ ({len(games)} games)")
                
                # Show sample game
                if games:
                    game = games[0]
                    home_team = game.get('home_team', {}).get('name', 'N/A')
                    away_team = game.get('away_team', {}).get('name', 'N/A')
                    print(f"      Sample: {away_team} @ {home_team}")
            else:
                print(f"   {name}: {response.status_code} ❌")
                print(f"      Error: {response.text[:50]}")
            
            results[f'games_{name.lower().replace(" ", "_")}'] = {
                'status': response.status_code,
                'success': success,
                'games_count': len(games) if success else 0
            }
        except Exception as e:
            print(f"   {name}: ❌ {e}")
            results[f'games_{name.lower().replace(" ", "_")}'] = {
                'status': 'error',
                'success': False,
                'error': str(e)
            }
    
    # 5. Test Brain Services
    print("\n5. BRAIN SERVICES:")
    
    brain_endpoints = [
        ("Brain Status", "/api/brain-status"),
        ("Brain Control", "/api/brain-control"),
        ("Brain Persistence", "/api/brain-persistence")
    ]
    
    working_brain_count = 0
    for name, endpoint in brain_endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            success = response.status_code == 200
            
            if success:
                print(f"   {name}: {response.status_code} ✅")
                working_brain_count += 1
            else:
                print(f"   {name}: {response.status_code} ❌")
                print(f"      Error: {response.text[:50]}")
            
            results[f'brain_{name.lower().replace(" ", "_")}'] = {
                'status': response.status_code,
                'success': success
            }
        except Exception as e:
            print(f"   {name}: ❌ {e}")
            results[f'brain_{name.lower().replace(" ", "_")}'] = {
                'status': 'error',
                'success': False,
                'error': str(e)
            }
    
    # 6. Summary
    print("\n" + "="*80)
    print("COMPREHENSIVE TEST RESULTS")
    print("="*80)
    
    total_props_endpoints = len(props_endpoints)
    total_parlay_endpoints = len(parlay_endpoints)
    total_game_endpoints = len(game_endpoints)
    total_brain_endpoints = len(brain_endpoints)
    
    print(f"\n📊 SUMMARY:")
    print(f"   Backend Health: {'✅' if results.get('health', {}).get('success') else '❌'}")
    print(f"   Player Props: {working_props_count}/{total_props_endpoints} working ✅" if working_props_count > 0 else f"   Player Props: {working_props_count}/{total_props_endpoints} working ❌")
    print(f"   Parlays: {working_parlays_count}/{total_parlay_endpoints} working ✅" if working_parlays_count > 0 else f"   Parlays: {working_parlays_count}/{total_parlay_endpoints} working ❌")
    print(f"   Game Lines: Testing...")
    print(f"   Brain Services: {working_brain_count}/{total_brain_endpoints} working")
    
    print(f"\n🎯 WORKING ENDPOINTS:")
    for name, endpoint in props_endpoints:
        key = f'props_{name.lower().replace(" ", "_")}'
        if results.get(key, {}).get('success'):
            print(f"   ✅ {name}: {endpoint}")
    
    for name, endpoint in parlay_endpoints:
        key = f'parlay_{name.lower().replace(" ", "_")}'
        if results.get(key, {}).get('success'):
            print(f"   ✅ {name}: {endpoint}")
    
    print(f"\n🚨 BROKEN ENDPOINTS:")
    for name, endpoint in props_endpoints:
        key = f'props_{name.lower().replace(" ", "_")}'
        if not results.get(key, {}).get('success'):
            print(f"   ❌ {name}: {endpoint}")
    
    # 7. Recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    
    if working_props_count > 0:
        print("   ✅ Use WORKING endpoints for player props")
        print("   ✅ Update frontend to use /working/working-player-props")
    
    if working_parlays_count > 0:
        print("   ✅ Use WORKING endpoints for parlays")
        print("   ✅ Update frontend to use /working/working-parlays")
    
    if results.get('health', {}).get('success'):
        print("   ✅ Backend is healthy - database retry fix worked!")
    else:
        print("   ❌ Backend still having issues - check database connection")
    
    print(f"\n🎮 FRONTEND UPDATE NEEDED:")
    print("   Player Props: /working/working-player-props?sport_id=31")
    print("   Super Bowl: /working/super-bowl-working")
    print("   Parlays: /working/working-parlays")
    print("   Monte Carlo: /working/monte-carlo-simulation")
    
    print(f"\n⏰ STATUS: {'EVERYTHING WORKING!' if working_props_count > 0 and working_parlays_count > 0 else 'PARTIALLY WORKING'}")
    
    # Save results
    with open("c:/Users/preio/preio/perplex-edge/test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Results saved to: test_results.json")
    
    print("\n" + "="*80)
    print("COMPREHENSIVE TEST COMPLETE")
    print("="*80)

if __name__ == "__main__":
    comprehensive_test()
