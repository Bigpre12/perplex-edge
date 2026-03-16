# diagnose_props.py
import asyncio
import os
import sys
import time

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

async def diagnose():
    print("--- Starting Props Diagnosis ---")
    start_time = time.time()
    try:
        from db.session import get_db
        from services.props_service import get_props_by_sport
        
        db_gen = get_db()
        db = next(db_gen)
        
        sports_to_test = [
            (30, "NBA (basketball_nba)"),
            (39, "NCAAB (basketball_ncaab)"),
            (53, "WNBA (basketball_wnba)"),
            (40, "MLB (baseball_mlb)")
        ]
        
        for sport_id, name in sports_to_test:
            print(f"\n--- {name} Diagnosis ---")
            print(f"Calling get_props_by_sport(sport_id={sport_id}, limit=5)...")
            result = await get_props_by_sport(sport_id=sport_id, limit=5, db=db)
            print(f"Success! Found {len(result.get('items', []))} items.")
            if result.get('items'):
                first_item = result['items'][0]
                print(f"First item player: {first_item['player']['name']}")
                print(f"First item stat type: {first_item.get('stat_type', 'N/A')}")
                print(f"First item sport_id verification: {first_item.get('sport_id') == sport_id} (Found: {first_item.get('sport_id')})")

    except Exception as e:
        print(f"Exception during diagnosis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(diagnose())
