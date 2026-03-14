class AsyncSession: pass
from fastapi import APIRouter, Depends, Body, HTTPException, status
from database import get_async_db
from models.users import PushSubscription
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone
from sqlalchemy import select
import os
import json
try:
    from pywebpush import webpush, WebPushException
except ImportError:
    webpush = None
    WebPushException = Exception

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

class PushMessage(BaseModel):
    title: str
    body: str

@router.post('/send')
async def send_push_notification(
    message: PushMessage,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Dispatch a push notification to all subscribed users.
    Requires VAPID_PRIVATE_KEY exported in environment.
    """
    vapid_private_key = os.environ.get("VAPID_PRIVATE_KEY")
    vapid_claims = {"sub": "mailto:admin@perplex.com"}

    if not webpush:
        return {"status": "error", "message": "pywebpush module not installed."}

    if not vapid_private_key:
        print("Warning: VAPID_PRIVATE_KEY not set. Push simulated.")
        return {"status": "simulated_success", "note": "Keys not configured for real push."}

    stmt = select(PushSubscription)
    result = await db.execute(stmt)
    subscriptions = result.scalars().all()
    
    success_count = 0
    failure_count = 0

    for sub in subscriptions:
        try:
            sub_info = {
                "endpoint": sub.endpoint,
                "keys": {
                    "p256dh": sub.p256dh,
                    "auth": sub.auth
                }
            }
            webpush(
                subscription_info=sub_info,
                data=json.dumps({"title": message.title, "body": message.body}),
                vapid_private_key=vapid_private_key,
                vapid_claims=vapid_claims
            )
            success_count += 1
        except WebPushException as ex:
            print("WebPushException:", repr(ex))
            failure_count += 1
        except Exception as e:
            print("Push exception:", repr(e))
            failure_count += 1

    return {
        "status": "completed", 
        "sent": success_count, 
        "failed": failure_count
    }
