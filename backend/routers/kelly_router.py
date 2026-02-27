from fastapi import APIRouter, Depends, Query, Body, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_async_db
from models.props import PropLine
from models.bets import BetLog
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy import select

router = APIRouter(prefix='/api/kelly', tags=['kelly'])

def american_to_decimal(odds: int) -> float:
    return (odds / 100 + 1) if odds > 0 else (100 / abs(odds) + 1)

def kelly_fraction(win_prob: float, decimal_odds: float, fraction: float = 0.25) -> float:
    b = decimal_odds - 1
    q = 1 - win_prob
    k = (b * win_prob - q) / b
    return max(round(k * fraction, 4), 0.0)

@router.get('/size/{prop_id}')
async def get_kelly_size(
    prop_id: int, 
    bankroll: float = Query(default=1000.0),
    side: str = Query(default='over'), 
    db: AsyncSession = Depends(get_async_db)
):
    stmt = select(PropLine).where(PropLine.id == prop_id)
    result = await db.execute(stmt)
    prop = result.scalar_one_or_none()
    
    if not prop:
        raise HTTPException(status_code=404, detail='Prop not found')
    
    # Use real-time L10 statistics from the database
    hit_rate = (getattr(prop, 'hit_rate_l10', 50) or 50) / 100
    
    odds = -110 # Default for mock
    
    decimal = american_to_decimal(odds)
    full_kelly = kelly_fraction(hit_rate, decimal, fraction=1.0)
    quarter_kelly = kelly_fraction(hit_rate, decimal, fraction=0.25)
    
    recommended_units = round(quarter_kelly * 10, 2)
    recommended_dollars = round(quarter_kelly * bankroll, 2)
    ev = round((hit_rate * (decimal - 1) - (1 - hit_rate)) * 100, 2)
    
    return {
        'prop_id': prop_id,
        'player': prop.player_name,
        'stat': prop.stat_type,
        'line': prop.line,
        'side': side,
        'win_probability': round(hit_rate * 100, 1),
        'odds': odds,
        'ev_pct': ev,
        'full_kelly_pct': round(full_kelly * 100, 2),
        'quarter_kelly_pct': round(quarter_kelly * 100, 2),
        'recommended_units': recommended_units,
        'recommended_dollars': recommended_dollars,
        'bankroll': bankroll,
        'size_label': 'MAX BET' if quarter_kelly >= 0.05 else 'STRONG' if quarter_kelly >= 0.03 else 'MODERATE' if quarter_kelly >= 0.015 else 'SMALL'
    }

@router.post('/bulk-size')
async def bulk_kelly(
    prop_ids: List[int] = Body(...), 
    bankroll: float = Body(default=1000.0),
    db: AsyncSession = Depends(get_async_db)
):
    results = []
    stmt = select(PropLine).where(PropLine.id.in_(prop_ids))
    result = await db.execute(stmt)
    props = result.scalars().all()
    
    for prop in props:
        hit_rate = (getattr(prop, 'hit_rate_l10', 50) or 50) / 100
        odds = -110
        decimal = american_to_decimal(odds)
        qk = kelly_fraction(hit_rate, decimal, 0.25)
        results.append({
            'prop_id': prop.id, 
            'player': prop.player_name, 
            'stat': prop.stat_type,
            'line': prop.line, 
            'recommended_units': round(qk * 10, 2),
            'recommended_dollars': round(qk * bankroll, 2)
        })
    
    total_units = round(sum(r['recommended_units'] for r in results), 2)
    return {'prop_count': len(results), 'total_units': total_units, 'picks': results}

@router.get('/hedge')
async def get_hedge_recommendation(
    prop_id: int,
    current_value: float,
    current_odds: int = -110,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Calculates if a hedge is recommended based on live game state.
    """
    stmt = select(PropLine).where(PropLine.id == prop_id)
    result = await db.execute(stmt)
    prop = result.scalar_one_or_none()
    
    if not prop:
        raise HTTPException(status_code=404, detail="Prop not found")
        
    line = prop.line
    progress = current_value / line
    
    # Simple logic: If progress > 75%, consider locking in profit (hedging)
    recommendation = "Hold Position"
    confidence = "High"
    
    if progress >= 0.9:
        recommendation = "Lock in profit: Hedge Under 15% of original stake."
    elif progress >= 0.75:
        recommendation = "Caution: Player pacing safely. Consider small hedge if odds are favorable."
    elif progress <= 0.2:
        recommendation = "Warning: Significant under-pacing. Hedge/Exit recommended."
        
    return {
        "prop_id": prop_id,
        "current_progress": round(progress * 100, 1),
        "recommendation": recommendation,
        "confidence": confidence,
        "live_odds": current_odds
    }
