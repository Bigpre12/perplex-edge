from fastapi import APIRouter, Depends, Body, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_async_db
from models.users import PushSubscription
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone
from sqlalchemy import select

router = APIRouter(prefix='/api/push', tags=['push'])

class SubscribePayload(BaseModel):
    user_id: str
    endpoint: str
    keys: dict

@router.post('/subscribe')
async def subscribe(
    payload: SubscribePayload = Body(...), 
    db: AsyncSession = Depends(get_async_db)
):
    stmt = select(PushSubscription).where(
        PushSubscription.user_id == int(payload.user_id),
        PushSubscription.endpoint == payload.endpoint
    )
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()
    
    if not existing:
        new_sub = PushSubscription(
            user_id=int(payload.user_id),
            endpoint=payload.endpoint,
            p256dh=payload.keys.get("p256dh"),
            auth=payload.keys.get("auth"),
            created_at=datetime.now(timezone.utc)
        )
        db.add(new_sub)
        await db.commit()
    return {'status': 'subscribed'}

@router.post('/unsubscribe')
async def unsubscribe(
    user_id: int, 
    endpoint: str, 
    db: AsyncSession = Depends(get_async_db)
):
    from sqlalchemy import delete
    stmt = delete(PushSubscription).where(
        PushSubscription.user_id == user_id,
        PushSubscription.endpoint == endpoint
    )
    await db.execute(stmt)
    await db.commit()
    return {'status': 'unsubscribed'}
