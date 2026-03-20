# backend/routers/api_tier_router.py
# White-label/developer API with token auth and rate limiting
from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from db.session import get_db
from models.prop import PropLine
from models.user import APIKey
from datetime import datetime, timedelta
from typing import Optional

router = APIRouter(tags=['api_tier'])

async def verify_api_key(x_api_key: str = Header(...), db: AsyncSession = Depends(get_db)) -> APIKey:
    stmt = select(APIKey).filter(APIKey.key == x_api_key, APIKey.is_active == True)
    result = await db.execute(stmt)
    key = result.scalar_one_or_none()
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
    await db.commit()
    return key

@router.get('/props')
async def api_get_props(sport: Optional[str] = None, min_confidence: int = Query(default=0),
                  limit: int = Query(default=50), api_key: APIKey = Depends(verify_api_key),
                  db: AsyncSession = Depends(get_db)):
    stmt = select(PropLine)
    if sport:
        stmt = stmt.where(PropLine.sport == sport)
    if min_confidence:
        stmt = stmt.where(PropLine.confidence_score >= min_confidence)
    stmt = stmt.order_by(PropLine.confidence_score.desc()).limit(limit)
    
    result = await db.execute(stmt)
    props = result.scalars().all()
    
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
async def api_top_picks(sport: Optional[str] = None, limit: int = Query(default=10),
                  api_key: APIKey = Depends(verify_api_key), db: AsyncSession = Depends(get_db)):
    if api_key.tier not in ['pro', 'enterprise']:
        raise HTTPException(status_code=403, detail='Pro or Enterprise plan required')
    stmt = select(PropLine).where(PropLine.confidence_score >= 65)
    if sport:
        stmt = stmt.where(PropLine.sport == sport)
    stmt = stmt.order_by(PropLine.confidence_score.desc()).limit(limit)
    
    result = await db.execute(stmt)
    props = result.scalars().all()
    
    return {'top_picks': [{'player': p.player_name, 'stat': p.stat_category, 'line': p.line,
                            'confidence': getattr(p, 'confidence_score', None),
                            'ev_pct': getattr(p, 'ev_pct', None)} for p in props]}
