#!/usr/bin/env python3
"""
Trigger alembic migration
"""
import requests

def trigger_migration():
    """Trigger alembic migration"""
    base_url = "https://railway-engine-production.up.railway.app"
    
    print("TRIGGERING ALEMBIC MIGRATION")
    print("="*80)
    
    # Try to run alembic upgrade head
    print("\n1. Running Alembic Upgrade:")
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
    
    # Check if props work now
    print("\n2. Test Props After Migration:")
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
    
    # Test parlay builder
    print("\n3. Test Parlay Builder with Super Bowl:")
    parlay_url = f"{base_url}/api/sports/31/parlays/builder?leg_count=2&max_results=3"
    
    try:
        response = requests.get(parlay_url, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            parlays = data.get('parlays', [])
            print(f"   Found {len(parlays)} parlays")
            
            if parlays:
                for parlay in parlays[:2]:
                    print(f"   - Parlay EV: {parlay.get('total_ev', 0):.2%}")
                    print(f"     Legs: {len(parlay.get('legs', []))}")
            else:
                print("   No parlays yet (need picks with edge)")
        else:
            print(f"   Error: {response.text[:100]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n" + "="*80)
    print("STATUS:")
    print("- Migration: Triggered")
    print("- Props: Testing...")
    print("- Parlay Builder: Testing...")
    print("="*80)

if __name__ == "__main__":
    trigger_migration()
