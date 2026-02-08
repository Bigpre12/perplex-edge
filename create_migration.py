#!/usr/bin/env python3
"""
Create migration to add missing columns
"""
import requests

def create_migration():
    """Create migration to add missing columns"""
    base_url = "https://railway-engine-production.up.railway.app"
    
    print("CREATING MIGRATION FOR MISSING COLUMNS")
    print("="*80)
    
    # Try to trigger alembic migration
    print("\n1. Trigger Alembic Migration:")
    migration_url = f"{base_url}/admin/alembic/upgrade/head"
    
    try:
        response = requests.post(migration_url, timeout=30)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Migration result: {data}")
        else:
            print(f"   Error: {response.text[:100]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Check if the column exists now
    print("\n2. Test Props After Migration:")
    props_url = f"{base_url}/api/sports/31/picks/player-props?limit=5"
    
    try:
        response = requests.get(props_url, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            props = data.get('items', [])
            print(f"   Found {len(props)} props")
            
            if props:
                for prop in props[:3]:
                    player = prop.get('player', {})
                    print(f"   - {player.get('name', 'N/A')}: {prop.get('stat_type', 'N/A')} {prop.get('line_value', 'N/A')}")
                    print(f"     Edge: {prop.get('edge', 0):.2%}")
            else:
                print("   Still no props found")
        else:
            print(f"   Error: {response.text[:100]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    create_migration()
