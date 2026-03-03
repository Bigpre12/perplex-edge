import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from models.users import User

async def test_db():
    print("Connecting to local SQLite engine...")
    engine = create_async_engine('sqlite+aiosqlite:///./perplex_local.db')
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    
    async with async_session() as session:
        try:
            print("Injecting test user...")
            user = User(email='test_admin@perplex.game', hashed_password='dummy')
            session.add(user)
            await session.commit()
            print("SUCCESS: Mock User Ingested. ORM Models are stable and active.")
        except Exception as e:
            print(f"FAILED: {e}")
            
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(test_db())
