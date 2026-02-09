#!/usr/bin/env python3
"""
Check if deployment has updated
"""
import requests

def check_deployment_update():
    """Check if deployment has updated"""
    base_url = "https://railway-engine-production.up.railway.app"
    
    print("CHECKING IF DEPLOYMENT HAS UPDATED")
    print("="*80)
    
    # Check OpenAPI for new endpoints
    print("\n1. Check OpenAPI for New Endpoints:")
    try:
        response = requests.get(f"{base_url}/openapi.json", timeout=10)
        if response.status_code == 200:
            data = response.json()
            paths = data.get("paths", {})
            
            # Check for our new endpoints
            has_sql = "/admin/sql" in paths
            has_stub = "/api/sports/{sport_id}/picks/player-props-stub" in paths
            
            print(f"   SQL endpoint deployed: {has_sql}")
            print(f"   Stub endpoint deployed: {has_stub}")
            
            if has_sql:
                print("   SUCCESS: SQL endpoint is deployed!")
                
                # Test SQL endpoint
                print("\n2. Test SQL Endpoint:")
                try:
                    response = requests.post(f"{base_url}/admin/sql", json={"query": "SELECT 1 as test;"}, timeout=10)
                    print(f"   Status: {response.status_code}")
                    
                    if response.status_code == 200:
                        data = response.json()
                        print(f"   SUCCESS: SQL endpoint working!")
                        
                        # Add the 9 CLV columns
                        print("\n3. Adding 9 CLV Columns:")
                        clv_columns = [
                            ("closing_odds", "NUMERIC(10, 4)"),
                            ("clv_percentage", "NUMERIC(10, 4)"),
                            ("roi_percentage", "NUMERIC(10, 4)"),
                            ("opening_odds", "NUMERIC(10, 4)"),
                            ("line_movement", "NUMERIC(10, 4)"),
                            ("sharp_money_indicator", "NUMERIC(10, 4)"),
                            ("best_book_odds", "NUMERIC(10, 4)"),
                            ("best_book_name", "VARCHAR(50)"),
                            ("ev_improvement", "NUMERIC(10, 4)")
                        ]
                        
                        for i, (col_name, col_type) in enumerate(clv_columns, 1):
                            sql = f"ALTER TABLE model_picks ADD COLUMN IF NOT EXISTS {col_name} {col_type};"
                            print(f"   {i}. Adding {col_name}...")
                            
                            try:
                                response = requests.post(f"{base_url}/admin/sql", json={"query": sql}, timeout=10)
                                print(f"      Status: {response.status_code}")
                                
                                if response.status_code == 200:
                                    result = response.json()
                                    print(f"      Result: {result}")
                                else:
                                    print(f"      Error: {response.text[:100]}")
                            except Exception as e:
                                print(f"      Error: {e}")
                            
                            # Small delay
                            import time
                            time.sleep(0.5)
                        
                        # Test picks immediately
                        print("\n4. Test Picks After Column Fix:")
                        test_url = f"{base_url}/api/sports/30/picks/player-props?limit=5"
                        
                        try:
                            response = requests.get(test_url, timeout=10)
                            print(f"   Status: {response.status_code}")
                            
                            if response.status_code == 200:
                                data = response.json()
                                props = data.get('items', [])
                                print(f"   SUCCESS! Found {len(props)} props")
                                
                                if props:
                                    print(f"   Sample prop:")
                                    prop = props[0]
                                    player = prop.get('player', {})
                                    print(f"   - {player.get('name', 'N/A')}: {prop.get('stat_type', 'N/A')} {prop.get('line_value', 'N/A')}")
                                    print(f"     Edge: {prop.get('edge', 0):.2%}")
                                    
                                    # Get total count
                                    total_url = f"{base_url}/api/sports/30/picks/player-props?limit=200"
                                    total_response = requests.get(total_url, timeout=10)
                                    if total_response.status_code == 200:
                                        total_data = total_response.json()
                                        total_props = total_data.get('items', [])
                                        print(f"\n   Total NBA props: {len(total_props)}")
                                        
                                        # Group by game
                                        game_props = {}
                                        for prop in total_props:
                                            game_id = prop.get('game_id')
                                            if game_id not in game_props:
                                                game_props[game_id] = []
                                            game_props[game_id].append(prop)
                                        
                                        print(f"   Props per game:")
                                        for game_id, game_prop_list in game_props.items():
                                            print(f"   Game {game_id}: {len(game_prop_list)} props")
                            else:
                                print(f"   Still error: {response.text[:100]}")
                        except Exception as e:
                            print(f"   Error: {e}")
                        
                        # Test NFL picks
                        print("\n5. Test NFL Super Bowl Picks:")
                        nfl_url = f"{base_url}/api/sports/31/picks/player-props?game_id=648&limit=5"
                        
                        try:
                            response = requests.get(nfl_url, timeout=10)
                            print(f"   Status: {response.status_code}")
                            
                            if response.status_code == 200:
                                data = response.json()
                                props = data.get('items', [])
                                print(f"   SUCCESS! Found {len(props)} NFL props")
                                
                                if props:
                                    print(f"   Sample NFL props:")
                                    for prop in props[:3]:
                                        player = prop.get('player', {})
                                        print(f"   - {player.get('name', 'N/A')}: {prop.get('stat_type', 'N/A')} {prop.get('line_value', 'N/A')}")
                            else:
                                print(f"   Error: {response.text[:100]}")
                        except Exception as e:
                            print(f"   Error: {e}")
                    else:
                        print(f"   Error: {response.text[:100]}")
                except Exception as e:
                    print(f"   Error: {e}")
            else:
                print("   SQL endpoint not yet deployed")
            
            if has_stub:
                print("   SUCCESS: Stub endpoint is deployed!")
                
                # Test stub endpoint
                print("\n6. Test Stub Endpoint:")
                try:
                    response = requests.get(f"{base_url}/api/sports/30/picks/player-props-stub", timeout=10)
                    print(f"   Status: {response.status_code}")
                    
                    if response.status_code == 200:
                        data = response.json()
                        props = data.get('items', [])
                        print(f"   SUCCESS: Found {len(props)} stub props")
                        
                        if props:
                            print(f"   Sample stub props:")
                            for prop in props[:3]:
                                player = prop.get('player', {})
                                print(f"   - {player.get('name', 'N/A')}: {prop.get('stat_type', 'N/A')} {prop.get('line_value', 'N/A')}")
                    else:
                        print(f"   Error: {response.text[:100]}")
                except Exception as e:
                    print(f"   Error: {e}")
            else:
                print("   Stub endpoint not yet deployed")
            
            # Count total endpoints
            print(f"\n   Total endpoints: {len(paths)}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n" + "="*80)
    print("DEPLOYMENT UPDATE STATUS:")
    print("- SQL Endpoint: Checking...")
    print("- Stub Endpoint: Checking...")
    print("- CLV Columns: Ready to add...")
    print("- NBA Picks: Ready to test...")
    print("- NFL Picks: Ready to test...")
    print("="*80)

if __name__ == "__main__":
    check_deployment_update()
