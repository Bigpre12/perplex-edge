# backend/routers/push_router.py
import json, os
from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from database import get_db
from models import PushSubscription, PropOdds
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

router = APIRouter(prefix='/api/push', tags=['push'])

class SubscribePayload(BaseModel):
    user_id: str
    endpoint: str
    keys: dict

@router.post('/subscribe')
def subscribe(payload: SubscribePayload = Body(...), db: Session = Depends(get_db)):
    existing = db.query(PushSubscription).filter(
        PushSubscription.user_id == payload.user_id,
        PushSubscription.endpoint == payload.endpoint
    ).first()
    if not existing:
        db.add(PushSubscription(
            user_id=payload.user_id,
            endpoint=payload.endpoint,
            keys_json=json.dumps(payload.keys),
            created_at=datetime.utcnow()
        ))
        db.commit()
    return {'status': 'subscribed'}

@router.post('/unsubscribe')
def unsubscribe(user_id: str, endpoint: str, db: Session = Depends(get_db)):
    db.query(PushSubscription).filter(
        PushSubscription.user_id == user_id,
        PushSubscription.endpoint == endpoint
    ).delete()
    db.commit()
    return {'status': 'unsubscribed'}
