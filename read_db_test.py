import asyncio
from sqlalchemy import text
from db.session import async_session_maker

async def check():
    async with async_session_maker() as session:
        # Check props_live
        res = await session.execute(text("SELECT COUNT(*), player_name FROM props_live GROUP BY player_name LIMIT 10;"))
        rows = res.fetchall()
        print("--- props_live scan ---")
        for row in rows:
            print(f"Count: {row[0]}, Player: '{row[1]}'")
            
        # Check if any player props exist
        res = await session.execute(text("SELECT COUNT(*) FROM props_live WHERE player_name != '';"))
        count = res.scalar()
        print(f"--- TOTAL PLAYER PROPS (non-empty name): {count} ---")

if __name__ == "__main__":
    asyncio.run(check())
