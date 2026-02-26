# backend/routers/referral_router.py
from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from database import get_db
from models import User, Referral
from datetime import datetime
import secrets

router = APIRouter(prefix='/api/referral', tags=['referral'])

@router.get('/my-code/{user_id}')
def get_referral_code(user_id: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {'error': 'User not found'}
    if not user.referral_code:
        user.referral_code = secrets.token_urlsafe(8).upper()
        db.commit()
    refs = db.query(Referral).filter(Referral.referrer_id == user_id, Referral.is_active == True).all()
    return {
        'code': user.referral_code,
        'share_url': f'https://lola.yourdomain.com?ref={user.referral_code}',
        'active_referrals': len(refs),
        'monthly_credit': len(refs) * 5,
        'referrals': [{'user': r.referred_email, 'joined': r.created_at.isoformat(), 'active': r.is_active} for r in refs]
    }

@router.post('/register')
def register_referral(referred_email: str = Body(...), referral_code: str = Body(...),
                       db: Session = Depends(get_db)):
    referrer = db.query(User).filter(User.referral_code == referral_code).first()
    if not referrer:
        return {'status': 'invalid_code'}
    existing = db.query(Referral).filter(Referral.referred_email == referred_email).first()
    if existing:
        return {'status': 'already_registered'}
    db.add(Referral(referrer_id=referrer.id, referred_email=referred_email,
                     is_active=False, created_at=datetime.utcnow()))
    db.commit()
    return {'status': 'registered', 'referrer': referrer.id}
