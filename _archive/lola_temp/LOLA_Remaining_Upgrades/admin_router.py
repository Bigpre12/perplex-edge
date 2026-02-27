# backend/routers/admin_router.py
from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User, BetLog, PropLine, PublicSlate
from datetime import datetime, timedelta
from collections import defaultdict
import os

router = APIRouter(prefix='/admin', tags=['admin'])
ADMIN_SECRET = os.getenv('ADMIN_SECRET_KEY', 'changeme')

def verify_admin(x_admin_key: str = Header(...)):
    if x_admin_key != ADMIN_SECRET:
        raise HTTPException(status_code=403, detail='Unauthorized')

@router.get('/dashboard')
def admin_dashboard(db: Session = Depends(get_db), _: None = Depends(verify_admin)):
    now = datetime.utcnow()
    day_ago  = now - timedelta(days=1)
    week_ago = now - timedelta(days=7)
    total_users = db.query(User).count()
    pro_users   = db.query(User).filter(User.tier == 'pro').count()
    dau         = db.query(BetLog.user_id).filter(BetLog.created_at >= day_ago).distinct().count()
    wau         = db.query(BetLog.user_id).filter(BetLog.created_at >= week_ago).distinct().count()
    bets_today  = db.query(BetLog).filter(BetLog.created_at >= day_ago).count()
    settled     = db.query(BetLog).filter(BetLog.created_at >= week_ago, BetLog.status != 'pending').all()
    hit_rate    = round(sum(1 for b in settled if b.status=='won') / max(len(settled),1) * 100, 1)
    total_props = db.query(PropLine).count()
    slates_today = db.query(PublicSlate).filter(PublicSlate.published_at >= day_ago).count()
    sport_bets  = defaultdict(int)
    for b in settled:
        sport_bets[b.sport] += 1
    return {
        'users': {'total': total_users, 'pro': pro_users, 'free': total_users - pro_users},
        'activity': {'dau': dau, 'wau': wau, 'bets_today': bets_today},
        'performance': {'settled_bets_7d': len(settled), 'hit_rate_7d': hit_rate},
        'content': {'active_props': total_props, 'slates_published_today': slates_today},
        'bets_by_sport': dict(sport_bets),
        'mrr_estimate': pro_users * 25,
        'generated_at': now.isoformat()
    }

@router.get('/top-props')
def top_tailed_props(db: Session = Depends(get_db), _: None = Depends(verify_admin)):
    props = db.query(PropLine).order_by(PropLine.confidence_score.desc()).limit(10).all()
    return [{'player':p.player_name,'sport':p.sport,'stat':p.stat_category,'line':p.line,'confidence':getattr(p,'confidence_score',None)} for p in props]
