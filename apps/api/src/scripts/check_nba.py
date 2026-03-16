import asyncio
from sqlalchemy import select
from db.session import async_session_maker
from models.prop import PropLine
from datetime import datetime, timezone

async def check_nba_props():
    async with async_session_maker() as session:
        stmt = select(PropLine).where(PropLine.sport_key == 'basketball_nba')
        res = await session.execute(stmt)
        props = res.scalars().all()
        
        print(f"Found {len(props)} PropLines for basketball_nba")
        none_count = len([p for p in props if p.start_time is None])
        print(f"PropLines with start_time=None: {none_count}")
        
        if props:
            print("\nTOP 5 RECORDS DETAIL:")
            for p in props[:5]:
                print(f"ID: {p.id} | Player: {p.player_name} | Team: {p.team} | Opp: {p.opponent} | Sport: {p.sport_key} | Start: {p.start_time} | Active: {p.is_active}")
            
            # Check for today's date specifically
            today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            today_props = [p for p in props if p.start_time and p.start_time.strftime("%Y-%m-%d") >= today_str]
            print(f"\nRecords starting TODAY or LATER: {len(today_props)}")
            if today_props:
                tp = today_props[0]
                print(f"Sample Today: {tp.player_name} | {tp.start_time}")

if __name__ == "__main__":
    asyncio.run(check_nba_props())
