#!/usr/bin/env python3
"""
Execute CLV columns addition and test picks
"""
import requests

def execute_clv_columns():
    """Execute CLV columns addition and test picks"""
    base_url = "https://railway-engine-production.up.railway.app"
    
    print("EXECUTING CLV COLUMNS ADDITION")
    print("="*80)
    
    # The 9 CLV columns to add
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
    
    print("\n1. Adding 9 CLV Columns:")
    print("   You're running these SQL commands:")
    for i, (col_name, col_type) in enumerate(clv_columns, 1):
        sql = f"ALTER TABLE model_picks ADD COLUMN IF NOT EXISTS {col_name} {col_type};"
        print(f"   {i}. {sql}")
    
    print("\n2. After running these commands, let's test the picks endpoint:")
    
    # Test picks endpoint
    print("\n3. Testing Picks Endpoint:")
    try:
        response = requests.get(f"{base_url}/api/sports/30/picks/player-props?limit=5", timeout=10)
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
        elif response.status_code == 500:
            print(f"   Still 500 error - CLV columns may not be added yet")
            print(f"   Error: {response.text[:100]}")
        else:
            print(f"   Error: {response.text[:100]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test NFL picks
    print("\n4. Testing NFL Super Bowl Picks:")
    try:
        response = requests.get(f"{base_url}/api/sports/31/picks/player-props?game_id=648&limit=5", timeout=10)
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
    
    # Test parlay builder
    print("\n5. Testing Parlay Builder:")
    try:
        parlay_url = f"{base_url}/api/sports/30/parlays/builder?leg_count=2&max_results=3"
        response = requests.get(parlay_url, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            parlays = data.get('parlays', [])
            print(f"   Found {len(parlays)} parlays")
            
            if parlays:
                print(f"   SUCCESS: Parlay Builder working!")
                for parlay in parlays[:2]:
                    print(f"   - Parlay EV: {parlay.get('total_ev', 0):.2%}")
                    print(f"     Model Status: {parlay.get('model_status', {}).get('status', 'N/A')}")
        else:
            print(f"   Error: {response.text[:100]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n" + "="*80)
    print("EXECUTION STATUS:")
    print("1. CLV Columns: Adding manually...")
    print("2. NBA Picks: Testing...")
    print("3. NFL Picks: Testing...")
    print("4. Parlay Builder: Testing...")
    print("="*80)
    
    print("\nNEXT STEPS:")
    print("1. Run the 9 ALTER TABLE commands")
    print("2. Test picks endpoint")
    print("3. If working, activate picks")
    print("4. Test parlay builder")
    print("5. Launch for Super Bowl!")
    
    print("\n" + "="*80)
    print("CLV COLUMNS: READY TO ADD")
    print("Run the commands and test the picks endpoint!")
    print("="*80)

if __name__ == "__main__":
    execute_clv_columns()
