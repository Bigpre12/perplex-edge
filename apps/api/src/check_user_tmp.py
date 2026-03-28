
import asyncio
import os
from sqlalchemy import select
from db.session import AsyncSessionLocal
from models.user import User

async def check_user():
    email = "brydsonpreion31@gmail.com"
    async with AsyncSessionLocal() as session:
        stmt = select(User).where(User.email == email)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        
        if user:
            print(f"USER_FOUND: {user.email}")
            print(f"ID: {user.id}")
            print(f"USERNAME: {user.username}")
            print(f"HAS_PASSWORD: {bool(user.hashed_password)}")
            print(f"TIER: {user.subscription_tier}")
            print(f"CLERK_ID: {user.clerk_id}")
            print(f"STRIPE_ID: {user.stripe_customer_id}")
        else:
            print("USER_NOT_FOUND")

if __name__ == "__main__":
    asyncio.run(check_user())
