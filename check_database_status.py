#!/usr/bin/env python3
"""
Check database status and try to fix props
"""
import requests

def check_database_status():
    """Check database status"""
    base_url = "https://railway-engine-production.up.railway.app"
    
    print("DATABASE STATUS CHECK")
    print("="*80)
    
    # Check admin quota
    print("\n1. Admin Quota Status:")
    quota_url = f"{base_url}/admin/quota"
    
    try:
        response = requests.get(quota_url, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Database quota: {data}")
        else:
            print(f"   Error: {response.text[:100]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Check if we can see any players
    print("\n2. Check NFL Players:")
    players_url = f"{base_url}/api/players?sport_id=31&limit=10"
    
    try:
        response = requests.get(players_url, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            players = data.get('items', [])
            print(f"   Found {len(players)} NFL players")
            
            # Look for QBs
            qbs = [p for p in players if 'quarterback' in p.get('position', '').lower()]
            print(f"   Quarterbacks: {len(qbs)}")
            
            for qb in qbs[:5]:
                print(f"   - {qb.get('name', 'N/A')} ({qb.get('team', {}).get('name', 'N/A')})")
        else:
            print(f"   Error: {response.text[:100]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Check markets for NFL
    print("\n3. Check NFL Markets:")
    markets_url = f"{base_url}/api/sports/31/markets"
    
    try:
        response = requests.get(markets_url, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            markets = data.get('items', [])
            print(f"   Found {len(markets)} markets")
            
            for market in markets[:10]:
                stat_type = market.get('stat_type', 'N/A')
                count = market.get('count', 0)
                print(f"   - {stat_type}: {count} picks")
        else:
            print(f"   Error: {response.text[:100]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Try to trigger a simple sync
    print("\n4. Try Simple Sync:")
    simple_sync_url = f"{base_url}/admin/jobs/sync-quota-safe"
    
    try:
        response = requests.post(simple_sync_url, timeout=15)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Sync result: {data}")
        else:
            print(f"   Error: {response.text[:100]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n" + "="*80)
    print("ISSUES IDENTIFIED:")
    print("1. Database integrity errors when syncing odds")
    print("2. No player props available for Super Bowl")
    print("3. Picks endpoints returning errors")
    print("\nRECOMMENDATIONS:")
    print("1. Check database schema for NFL props")
    print("2. Manually import Super Bowl props if needed")
    print("3. Focus on fixing odds sync for future games")
    print("="*80)

if __name__ == "__main__":
    check_database_status()
