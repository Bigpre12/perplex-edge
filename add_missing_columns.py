#!/usr/bin/env python3
"""
Add missing columns to model_picks table
"""
import requests

def add_missing_columns():
    """Add missing columns to model_picks table"""
    base_url = "https://railway-engine-production.up.railway.app"
    
    print("ADDING MISSING COLUMNS TO MODEL_PICKS TABLE")
    print("="*80)
    
    # SQL to add missing columns
    sql_statements = [
        "ALTER TABLE model_picks ADD COLUMN IF NOT EXISTS closing_odds NUMERIC(10, 4);",
        "ALTER TABLE model_picks ADD COLUMN IF NOT EXISTS clv_percentage NUMERIC(10, 4);",
        "ALTER TABLE model_picks ADD COLUMN IF NOT EXISTS roi_percentage NUMERIC(10, 4);",
        "ALTER TABLE model_picks ADD COLUMN IF NOT EXISTS opening_odds NUMERIC(10, 4);",
        "ALTER TABLE model_picks ADD COLUMN IF NOT EXISTS line_movement NUMERIC(10, 4);",
        "ALTER TABLE model_picks ADD COLUMN IF NOT EXISTS sharp_money_indicator NUMERIC(10, 4);",
        "ALTER TABLE model_picks ADD COLUMN IF NOT EXISTS best_book_odds NUMERIC(10, 4);",
        "ALTER TABLE model_picks ADD COLUMN IF NOT EXISTS best_book_name VARCHAR(50);",
        "ALTER TABLE model_picks ADD COLUMN IF NOT EXISTS ev_improvement NUMERIC(10, 4);"
    ]
    
    print("\n1. Adding Missing Columns:")
    for i, sql in enumerate(sql_statements, 1):
        print(f"   {i}. {sql}")
        
        # Try to execute via admin endpoint if available
        try:
            # Check if there's an admin SQL endpoint
            response = requests.post(f"{base_url}/admin/sql", json={"query": sql}, timeout=10)
            if response.status_code == 200:
                print(f"      Success: {response.json()}")
            else:
                print(f"      Failed: {response.status_code}")
        except:
            print(f"      No SQL endpoint available")
    
    print("\n2. Test Picks After Column Addition:")
    test_url = f"{base_url}/api/sports/30/picks/player-props?limit=5"
    
    try:
        response = requests.get(test_url, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            props = data.get('items', [])
            print(f"   Found {len(props)} props - SUCCESS!")
            
            if props:
                print(f"   Sample prop:")
                prop = props[0]
                player = prop.get('player', {})
                print(f"   - {player.get('name', 'N/A')}: {prop.get('stat_type', 'N/A')} {prop.get('line_value', 'N/A')}")
                print(f"     Edge: {prop.get('edge', 0):.2%}")
        else:
            print(f"   Still error: {response.text[:100]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n" + "="*80)
    print("STATUS:")
    print("- Columns added: Testing...")
    print("- Picks endpoint: Testing...")
    print("="*80)

if __name__ == "__main__":
    add_missing_columns()
