from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_db
from models.user import User

@router.get("/me")
async def me(db: AsyncSession = Depends(get_db)):
    try:
        stmt = select(User).limit(1)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        if not user:
            user = User(username="demo-user", email="demo@example.com", subscription_tier="pro")
            db.add(user)
            await db.commit()
            await db.refresh(user)
        return user
    except Exception:
        return {"username": "demo-user", "email": "demo@example.com", "subscription_tier": "pro"}
