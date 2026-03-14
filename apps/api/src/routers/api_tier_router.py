# backend/routers/api_tier_router.py
# White-label/developer API with token auth and rate limiting
from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from models.props import PropLine
from models.users import APIKey
from datetime import datetime, timedelta
from typing import Optional

router = APIRouter(tags=['api_tier'])

def verify_api_key(x_api_key: str = Header(...), db: Session = Depends(get_db)) -> APIKey:
    key = db.query(APIKey).filter(APIKey.key == x_api_key, APIKey.is_active == True).first()
    if not key:
        raise HTTPException(status_code=401, detail='Invalid or inactive API key')
    if key.expires_at and key.expires_at < datetime.utcnow():
        raise HTTPException(status_code=401, detail='API key expired')
    # Rate limiting
    window_start = datetime.utcnow() - timedelta(hours=1)
    if key.last_reset and key.last_reset < window_start:
        key.requests_this_hour = 0
        key.last_reset = datetime.utcnow()
    if (key.requests_this_hour or 0) >= (key.rate_limit_per_hour or 500):
        raise HTTPException(status_code=429, detail='Rate limit exceeded')
    key.requests_this_hour = (key.requests_this_hour or 0) + 1
    key.total_requests = (key.total_requests or 0) + 1
    key.last_used = datetime.utcnow()
    db.commit()
    return key

@router.get('/props')
def api_get_props(sport: Optional[str] = None, min_confidence: int = Query(default=0),
                  limit: int = Query(default=50), api_key: APIKey = Depends(verify_api_key),
                  db: Session = Depends(get_db)):
    q = db.query(PropLine)
    if sport:
        q = q.filter(PropLine.sport == sport)
    if min_confidence:
        q = q.filter(PropLine.confidence_score >= min_confidence)
    props = q.order_by(PropLine.confidence_score.desc()).limit(limit).all()
    return {
        'count': len(props),
        'api_key_tier': api_key.tier,
        'props': [{
            'player': p.player_name, 'sport': p.sport,
            'stat': p.stat_category, 'line': p.line,
            'confidence': getattr(p, 'confidence_score', None),
            'hit_rate_l10': getattr(p, 'hit_rate_l10', None),
            'ev_pct': getattr(p, 'ev_pct', None),
            'dvp_label': getattr(p, 'dvp_label', None),
            'projection': getattr(p, 'projection', None)
        } for p in props]
    }

@router.get('/top-picks')
def api_top_picks(sport: Optional[str] = None, limit: int = Query(default=10),
                  api_key: APIKey = Depends(verify_api_key), db: Session = Depends(get_db)):
    if api_key.tier not in ['pro', 'enterprise']:
        raise HTTPException(status_code=403, detail='Pro or Enterprise plan required')
    q = db.query(PropLine).filter(PropLine.confidence_score >= 65)
    if sport:
        q = q.filter(PropLine.sport == sport)
    props = q.order_by(PropLine.confidence_score.desc()).limit(limit).all()
    return {'top_picks': [{'player': p.player_name, 'stat': p.stat_category, 'line': p.line,
                            'confidence': getattr(p, 'confidence_score', None),
                            'ev_pct': getattr(p, 'ev_pct', None)} for p in props]}
