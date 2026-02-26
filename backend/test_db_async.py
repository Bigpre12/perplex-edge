import asyncio
from database import async_session_maker
from models.users import User
from sqlalchemy import select

async def test_async_db():
    print("Testing Async DB connection...")
    async with async_session_maker() as session:
        try:
            stmt = select(User).limit(1)
            print("Executing statement...")
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()
            print(f"Result: {user}")
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_async_db())
