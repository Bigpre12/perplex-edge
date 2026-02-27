# backend/routers/kelly_router.py
from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.orm import Session
from database import get_db
from models import PropLine, BetLog
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix='/api/kelly', tags=['kelly'])

def american_to_decimal(odds: int) -> float:
    return (odds / 100 + 1) if odds > 0 else (100 / abs(odds) + 1)

def kelly_fraction(win_prob: float, decimal_odds: float, fraction: float = 0.25) -> float:
    b = decimal_odds - 1
    q = 1 - win_prob
    k = (b * win_prob - q) / b
    return max(round(k * fraction, 4), 0.0)

@router.get('/size/{prop_id}')
def get_kelly_size(prop_id: str, bankroll: float = Query(default=1000.0),
                   side: str = Query(default='over'), db: Session = Depends(get_db)):
    prop = db.query(PropLine).filter(PropLine.id == prop_id).first()
    if not prop:
        return {'error': 'Prop not found'}
    hit_rate = (getattr(prop, 'hit_rate_l10', None) or 50) / 100
    odds = getattr(prop, 'book_over_odds', -110) if side == 'over' else getattr(prop, 'book_under_odds', -110)
    if not odds:
        odds = -110
    decimal = american_to_decimal(odds)
    full_kelly = kelly_fraction(hit_rate, decimal, fraction=1.0)
    quarter_kelly = kelly_fraction(hit_rate, decimal, fraction=0.25)
    recommended_units = round(quarter_kelly * 10, 2)
    recommended_dollars = round(quarter_kelly * bankroll, 2)
    ev = round((hit_rate * (decimal - 1) - (1 - hit_rate)) * 100, 2)
    return {
        'prop_id': prop_id,
        'player': prop.player_name,
        'stat': prop.stat_category,
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
def bulk_kelly(prop_ids: list = Body(...), bankroll: float = Body(default=1000.0),
               db: Session = Depends(get_db)):
    results = []
    for pid in prop_ids:
        prop = db.query(PropLine).filter(PropLine.id == pid).first()
        if not prop:
            continue
        hit_rate = (getattr(prop, 'hit_rate_l10', None) or 50) / 100
        odds = getattr(prop, 'book_over_odds', -110) or -110
        decimal = american_to_decimal(odds)
        qk = kelly_fraction(hit_rate, decimal, 0.25)
        results.append({'prop_id': pid, 'player': prop.player_name, 'stat': prop.stat_category,
                         'line': prop.line, 'recommended_units': round(qk * 10, 2),
                         'recommended_dollars': round(qk * bankroll, 2)})
    total_units = round(sum(r['recommended_units'] for r in results), 2)
    return {'prop_count': len(results), 'total_units': total_units, 'picks': results}
