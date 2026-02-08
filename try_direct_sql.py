#!/usr/bin/env python3
"""
Try direct SQL to add column
"""
import requests

def try_direct_sql():
    """Try direct SQL to add column"""
    base_url = "https://railway-engine-production.up.railway.app"
    
    print("TRYING DIRECT SQL TO ADD COLUMN")
    print("="*80)
    
    # Try to add column directly
    print("\n1. Add closing_odds Column:")
    sql_url = f"{base_url}/admin/sql"
    
    sql = """
    ALTER TABLE model_picks ADD COLUMN IF NOT EXISTS closing_odds FLOAT;
    """
    
    try:
        response = requests.post(sql_url, json={"query": sql}, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   SQL result: {data}")
        else:
            print(f"   Error: {response.text[:100]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Check if props work now
    print("\n2. Test Props After SQL:")
    props_url = f"{base_url}/api/sports/31/picks/player-props?game_id=648&limit=5"
    
    try:
        response = requests.get(props_url, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            props = data.get('items', [])
            print(f"   Found {len(props)} props")
            
            if props:
                # Look for QB props
                qb_props = []
                for prop in props:
                    player_name = prop.get('player', {}).get('name', '').lower()
                    if 'maye' in player_name or 'darnold' in player_name:
                        qb_props.append(prop)
                
                print(f"\n   QB Props ({len(qb_props)}):")
                for prop in qb_props:
                    player = prop.get('player', {})
                    print(f"   - {player.get('name', 'N/A')}: {prop.get('stat_type', 'N/A')} {prop.get('line_value', 'N/A')} ({prop.get('side', 'N/A')})")
                    print(f"     Edge: {prop.get('edge', 0):.2%}")
                    print(f"     Confidence: {prop.get('confidence_score', 0):.2%}")
            else:
                print("   No props found")
        else:
            print(f"   Error: {response.text[:100]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    try_direct_sql()
