import asyncio
from database import async_session_maker
from services.contest_service import contest_service

async def test_get_leaderboard():
    async with async_session_maker() as db:
        res = await contest_service.get_leaderboard(db)
        print(res)

if __name__ == "__main__":
    asyncio.run(test_get_leaderboard())
