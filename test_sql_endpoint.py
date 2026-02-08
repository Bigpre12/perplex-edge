#!/usr/bin/env python3
"""
Test SQL endpoint to add columns
"""
import requests

def test_sql_endpoint():
    """Test SQL endpoint to add columns"""
    base_url = "https://railway-engine-production.up.railway.app"
    
    print("TESTING SQL ENDPOINT TO ADD COLUMNS")
    print("="*80)
    
    # Test SQL endpoint with a simple query first
    print("\n1. Test SQL Endpoint:")
    test_sql = "SELECT 1 as test;"
    
    try:
        response = requests.post(f"{base_url}/admin/sql", json={"query": test_sql}, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Result: {data}")
        else:
            print(f"   Error: {response.text[:100]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Add missing columns
    print("\n2. Adding Missing Columns:")
    sql_columns = [
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
    
    for i, sql in enumerate(sql_columns, 1):
        print(f"\n   {i}. Adding column...")
        try:
            response = requests.post(f"{base_url}/admin/sql", json={"query": sql}, timeout=10)
            print(f"      Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"      Result: {data}")
            else:
                print(f"      Error: {response.text[:100]}")
        except Exception as e:
            print(f"      Error: {e}")
    
    # Test picks after adding columns
    print("\n3. Test Picks After Adding Columns:")
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
    print("- SQL endpoint: Testing...")
    print("- Columns added: Testing...")
    print("- Picks endpoint: Testing...")
    print("="*80)

if __name__ == "__main__":
    test_sql_endpoint()
