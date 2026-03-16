import asyncio
import os
import sys
from datetime import datetime, timezone, timedelta

# Add src to path
sys.path.append(os.getcwd())

from db.session import async_session_maker
from models.prop import PropLine, PropOdds
from sqlalchemy import select

async def check():
    try:
        async with async_session_maker() as db:
            sport = "basketball_nba"
            now = datetime.now(timezone.utc)
            print(f"DEBUG: Current UTC time: {now}")
            
            # Simple query first
            stmt_simple = select(PropLine).where(PropLine.sport_key == sport).limit(5)
            res_simple = await db.execute(stmt_simple)
            all_raw = res_simple.scalars().all()
            print(f"DEBUG: Total raw PropLines for {sport}: {len(all_raw)}")
            for p in all_raw:
                print(f"  - Player: {p.player_name}, Start: {p.start_time}")

            # Time-filtered query
            stmt = select(PropLine).where(
                PropLine.sport_key == sport,
                (PropLine.start_time >= now - timedelta(hours=24)) | (PropLine.start_time == None)
            ).limit(10)
            
            res = await db.execute(stmt)
            db_props = res.scalars().all()
            print(f"DEBUG: Filtered DB props found: {len(db_props)}")
            
            for dp in db_props[:5]:
                odds_stmt = select(PropOdds).where(PropOdds.prop_line_id == dp.id)
                odds_res = await db.execute(odds_stmt)
                book_odds = odds_res.scalars().all()
                print(f"  - Prop ID {dp.id}: {len(book_odds)} odds entries")

    except Exception as e:
        import traceback
        print(f"ERROR: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check())
