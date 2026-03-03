# backend/utils/feature_gate.py
# Whop webhook handler + in-app feature gating
from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import User
import hmac, hashlib, os, json

router = APIRouter(prefix='/webhooks', tags=['webhooks'])

WHOP_SECRET = os.getenv('WHOP_WEBHOOK_SECRET')

PRO_FEATURES = [
    'kelly_sizing', 'smart_money_signal', 'sgp_builder', 'whale_watcher',
    'clv_tracker', 'alternate_lines', 'kalshi_crossref', 'api_access'
]

def verify_whop_signature(payload: bytes, signature: str) -> bool:
    expected = hmac.new(WHOP_SECRET.encode(), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature.replace('sha256=', ''))

@router.post('/whop')
async def whop_webhook(request: Request, db: Session = Depends(get_db)):
    body = await request.body()
    sig = request.headers.get('X-Whop-Signature', '')
    if not verify_whop_signature(body, sig):
        raise HTTPException(status_code=401, detail='Invalid signature')
    event = json.loads(body)
    action = event.get('action')
    user_email = event.get('data', {}).get('user', {}).get('email')
    plan = event.get('data', {}).get('product', {}).get('name', '').lower()
    if not user_email:
        return {'status': 'ignored'}
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        return {'status': 'user_not_found'}
    if action in ['membership.went_valid', 'membership.was_created']:
        user.tier = 'pro' if 'pro' in plan else 'basic'
        user.whop_active = True
    elif action in ['membership.went_invalid', 'membership.was_deleted']:
        user.tier = 'free'
        user.whop_active = False
    db.commit()
    return {'status': 'updated', 'user': user_email, 'tier': user.tier}

def require_pro(user_tier: str, feature: str):
    if feature in PRO_FEATURES and user_tier not in ['pro', 'enterprise']:
        raise HTTPException(status_code=403, detail=f'{feature} requires Pro plan')
