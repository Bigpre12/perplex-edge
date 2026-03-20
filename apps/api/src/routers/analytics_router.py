# backend/routers/analytics_router.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from db.session import get_db
from models.bet import BetLog
from models.prop import PropLine
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Optional

router = APIRouter(tags=["analytics"])

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

@router.get('/ev-distribution')
async def ev_distribution(sport: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    try:
        stmt = select(PropLine)
        if sport:
            stmt = stmt.where(PropLine.sport == sport)
        result = await db.execute(stmt)
        props = result.scalars().all()
        buckets = defaultdict(int)
        labels = ['-10+','-5 to -10','-2 to -5','0 to -2','0 to 2','2 to 5','5 to 10','10+']
        for p in props:
            ev = getattr(p, 'ev_pct', None)
            if ev is None:
                continue
            if ev >= 10: buckets['10+'] += 1
            elif ev >= 5: buckets['5 to 10'] += 1
            elif ev >= 2: buckets['2 to 5'] += 1
            elif ev >= 0: buckets['0 to 2'] += 1
            elif ev >= -2: buckets['0 to -2'] += 1
            elif ev >= -5: buckets['-2 to -5'] += 1
            elif ev >= -10: buckets['-5 to -10'] += 1
            else: buckets['-10+'] += 1
        return {'total_props': len(props),
                'distribution': [{'bucket': l, 'count': buckets[l]} for l in labels],
                'positive_ev_count': sum(buckets[l] for l in ['0 to 2','2 to 5','5 to 10','10+']),
                'high_ev_count': buckets['5 to 10'] + buckets['10+']}
    except Exception:
        return {'total_props': 0, 'distribution': [], 'positive_ev_count': 0, 'high_ev_count': 0}

@router.get('/win-rate-breakdown/{user_id}')
async def win_rate_breakdown(user_id: str, days: int = Query(default=30), db: AsyncSession = Depends(get_db)):
    try:
        since = datetime.utcnow() - timedelta(days=days)
        stmt = select(BetLog).filter(BetLog.user_id == user_id,
                                        BetLog.created_at >= since, BetLog.status != 'pending')
        result = await db.execute(stmt)
        bets = result.scalars().all()
        by_sport = defaultdict(lambda: {'w':0,'t':0})
        by_stat  = defaultdict(lambda: {'w':0,'t':0})
        by_side  = defaultdict(lambda: {'w':0,'t':0})
        for b in bets:
            w = 1 if b.status == 'won' else 0
            by_sport[b.sport]['w']+=w; by_sport[b.sport]['t']+=1
            by_stat[b.stat_category]['w']+=w; by_stat[b.stat_category]['t']+=1
            by_side[b.side]['w']+=w; by_side[b.side]['t']+=1
        def fmt(d): return [{'label':k,'wins':v['w'],'bets':v['t'],'hit_rate':round(v['w']/v['t']*100,1)} for k,v in d.items() if v['t']>0]
        return {'by_sport': fmt(by_sport), 'by_stat_category': fmt(by_stat), 'by_side': fmt(by_side)}
    except Exception:
        return {'by_sport': [], 'by_stat_category': [], 'by_side': []}

@router.get('/confidence-calibration/{user_id}')
async def confidence_calibration(user_id: str, db: AsyncSession = Depends(get_db)):
    try:
        stmt = select(BetLog).filter(BetLog.user_id == user_id, BetLog.status != 'pending',
                                        BetLog.confidence_at_bet != None)
        result = await db.execute(stmt)
        bets = result.scalars().all()
        buckets = defaultdict(lambda: {'w':0,'t':0})
        for b in bets:
            bucket = (int(b.confidence_at_bet) // 10) * 10
            buckets[bucket]['t'] += 1
            if b.status == 'won':
                buckets[bucket]['w'] += 1
        rows = []
        for conf in sorted(buckets.keys()):
            v = buckets[conf]
            actual = round(v['w']/v['t']*100,1) if v['t']>0 else None
            rows.append({'confidence_range':f'{conf}-{conf+9}','predicted_pct':conf+5,'actual_pct':actual,'bets':v['t']})
        return {'calibration': rows,
                'verdict': 'Well calibrated' if all(abs((r['actual_pct'] or 0)-(r['predicted_pct'] or 0))<10 for r in rows) else 'Needs recalibration'}
    except Exception:
        return {'calibration': [], 'verdict': 'Unknown'}
