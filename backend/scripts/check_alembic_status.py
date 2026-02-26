#!/usr/bin/env python3
"""
Check Alembic migration status and provide reset commands
"""
import requests

def check_alembic_status():
    """Check Alembic migration status and provide reset commands"""
    base_url = "https://railway-engine-production.up.railway.app"
    
    print("CHECKING ALEMBIC MIGRATION STATUS")
    print("="*80)
    
    print("\n1. Check Current Migration Version:")
    try:
        # Try to get migration status via admin endpoint if available
        response = requests.post(f"{base_url}/admin/sql", 
                                 json={"query": "SELECT * FROM alembic_version;"}, 
                                 timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            rows = data.get('rows', [])
            print(f"   Current migration version(s):")
            for row in rows:
                print(f"   - {row}")
        else:
            print(f"   Error: {response.text[:100]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n2. Check Migration History:")
    try:
        response = requests.post(f"{base_url}/admin/sql", 
                                 json={"query": "SELECT version_num, is_head FROM alembic_version ORDER BY version_num;"}, 
                                 timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            rows = data.get('rows', [])
            print(f"   Migration history:")
            for row in rows:
                print(f"   - Version {row['version_num']}: {'Head' if row['is_head'] else 'Not Head'}")
        else:
            print(f"   Error: {response.text[:100]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n3. Check if CLV Columns Exist:")
    try:
        response = requests.post(f"{base_url}/admin/sql", 
                                 json={"query": "SELECT column_name FROM information_schema.columns WHERE table_name = 'model_picks' AND column_name IN ('closing_odds', 'clv_percentage', 'roi_percentage', 'opening_odds', 'line_movement', 'sharp_money_indicator', 'best_book_odds', 'best_book_name', 'ev_improvement') ORDER BY column_name;"}, 
                                 timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            rows = data.get('rows', [])
            print(f"   CLV columns found:")
            for row in rows:
                print(f"   - {row['column_name']}: {row['data_type']}")
            
            if len(rows) == 9:
                print("   SUCCESS: All 9 CLV columns exist!")
            else:
                print(f"   WARNING: Only {len(rows)}/9 CLV columns found")
        else:
            print(f"   Error: {response.text[:100]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n" + "="*80)
    print("RESET COMMANDS:")
    print("If migrations are stuck, run these commands:")
    print("\n1. Check current version:")
    print("   SELECT * FROM alembic_version;")
    
    print("\n2. Delete to reset (WARNING: This will lose migration history):")
    print("   DELETE FROM alembic_version;")
    
    print("\n3. After reset, run upgrade:")
    print("   alembic upgrade heads")
    
    print("\n4. Or stamp to a specific version:")
    print("   alembic stamp 20260207_010000")
    print("   alembic upgrade heads")
    
    print("\n" + "="*80)
    print("MIGRATION STATUS:")
    print("- Current version: Checking...")
    print("- CLV columns: Checking...")
    print("- Reset commands: Ready if needed")
    print("="*80)

if __name__ == "__main__":
    check_alembic_status()
