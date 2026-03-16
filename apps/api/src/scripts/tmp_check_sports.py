import asyncio
from sqlalchemy import text
from db.session import async_session_maker

async def check():
    async with async_session_maker() as s:
        try:
            res = await s.execute(text("SELECT id, name, key FROM sports"))
            for r in res.mappings():
                print(f"ID: {r['id']}, Name: {r['name']}, Key: {r['key']}")
        except Exception as e:
            print("Error:", e)

if __name__ == "__main__":
    asyncio.run(check())
