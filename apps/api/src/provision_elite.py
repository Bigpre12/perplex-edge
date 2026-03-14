class AsyncSession: pass
import asyncio
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, update
import os
import sys

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models.users import User
from services.auth_service import auth_service
from config import settings

async def provision():
    # Standard SQLite path for the app
    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "perplex_local.db"))
    DATABASE_URL = f"sqlite+aiosqlite:///{db_path}"
    
    print(f"Connecting to {DATABASE_URL}")
    engine = create_async_engine(DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        email = "eliten@perplex.edge"
        password = "elite123"
        username = "elite_tester"
        
        print(f"Hashing password '{password}'...")
        try:
            hashed_pw = auth_service.get_password_hash(password)
            print(f"Hashed OK: {hashed_pw[:10]}...")
        except Exception as e:
            print(f"HASHING FAILED: {e}")
            return

        try:
            # Check if user exists
            stmt = select(User).where(User.email == email)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()
            
            if user:
                print(f"User {email} exists. Updating password and tier...")
                user.hashed_password = hashed_pw
                user.subscription_tier = "elite"
                user.is_active = True
            else:
                print(f"Creating new user {email} with tier 'elite'...")
                user = User(
                    username=username,
                    email=email,
                    hashed_password=hashed_pw,
                    subscription_tier="elite",
                    is_active=True
                )
                session.add(user)
                
            await session.commit()
            print("Database updated successfully.")
        except Exception as e:
            print(f"DATABASE UPDATE FAILED: {e}")

if __name__ == "__main__":
    asyncio.run(provision())
