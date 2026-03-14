import asyncio
from database import async_session_maker
from services.contest_service import contest_service

async def test_get_leaderboard():
    async with async_session_maker() as db:
        res = await contest_service.get_global_leaderboard(db)
        print(f"Global Leaderboard: {res}")
        
        # Test contest leaderboard (mocking ID 1)
        res_contest = await contest_service.get_contest_leaderboard(db, contest_id=1)
        print(f"Contest Leaderboard (ID 1): {res_contest}")

if __name__ == "__main__":
    asyncio.run(test_get_leaderboard())
