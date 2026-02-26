# backend/routers/sgp_router.py
# Same-Game Parlay builder with correlation scoring
from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from database import get_db
from models import PropLine
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix='/api/sgp', tags=['sgp'])

# Correlation matrix: positive = legs help each other, negative = legs hurt each other
CORRELATION_MAP = {
    ('passing_yards', 'receiving_yards'): 0.65,
    ('passing_yards', 'receptions'): 0.60,
    ('passing_yards', 'passing_tds'): 0.55,
    ('passing_tds', 'receiving_tds'): 0.50,
    ('passing_yards', 'rushing_yards'): -0.30,
    ('rushing_yards', 'receiving_yards'): -0.20,
    ('points', 'assists'): 0.40,
    ('points', 'rebounds'): 0.20,
    ('assists', 'rebounds'): 0.15,
    ('pts_reb_ast', 'points'): 0.80,
    ('pts_reb_ast', 'assists'): 0.75,
    ('goals', 'shots'): 0.60,
    ('goals', 'assists'): 0.10,
    ('hits', 'total_bases'): 0.70,
    ('home_runs', 'total_bases'): 0.85,
}

def get_correlation(stat_a: str, stat_b: str) -> float:
    key = tuple(sorted([stat_a, stat_b]))
    return CORRELATION_MAP.get(key, 0.0)

def same_game_check(legs: list) -> bool:
    game_ids = set(l.get('game_id') for l in legs if l.get('game_id'))
    return len(game_ids) == 1

class SGPLeg(BaseModel):
    prop_id: str
    side: str
    game_id: str = None

@router.post('/build')
def build_sgp(legs: List[SGPLeg] = Body(...), db: Session = Depends(get_db)):
    props = []
    for leg in legs:
        p = db.query(PropLine).filter(PropLine.id == leg.prop_id).first()
        if p:
            props.append({'prop': p, 'side': leg.side, 'game_id': leg.game_id})
    if not props:
        return {'error': 'No valid props found'}
    correlations = []
    total_corr = 0.0
    for i in range(len(props)):
        for j in range(i + 1, len(props)):
            a = props[i]['prop']
            b = props[j]['prop']
            same_team = getattr(a, 'team', None) == getattr(b, 'team', None)
            corr = get_correlation(a.stat_category, b.stat_category)
            if not same_team and corr > 0:
                corr = corr * 0.3
            correlations.append({
                'leg_a': a.player_name, 'stat_a': a.stat_category,
                'leg_b': b.player_name, 'stat_b': b.stat_category,
                'same_team': same_team,
                'correlation': round(corr, 3),
                'label': 'POSITIVE' if corr > 0.3 else 'NEUTRAL' if corr >= -0.1 else 'NEGATIVE'
            })
            total_corr += corr
    import math
    base_prob = 1.0
    for p in props:
        hr = (getattr(p['prop'], 'hit_rate_l10', None) or 50) / 100
        base_prob *= hr
    adjusted_prob = min(base_prob * (1 + total_corr * 0.1), 0.99)
    implied_odds = round((1 / adjusted_prob - 1) * 100)
    return {
        'leg_count': len(props),
        'legs': [{'player': p['prop'].player_name, 'stat': p['prop'].stat_category, 'line': p['prop'].line, 'side': p['side']} for p in props],
        'correlations': correlations,
        'total_correlation_score': round(total_corr, 3),
        'base_win_prob': round(base_prob * 100, 2),
        'adjusted_win_prob': round(adjusted_prob * 100, 2),
        'implied_american_odds': f'+{implied_odds}' if implied_odds >= 0 else str(implied_odds),
        'sgp_grade': 'A' if total_corr >= 0.5 else 'B' if total_corr >= 0.2 else 'C' if total_corr >= 0 else 'D'
    }

@router.get('/correlation-matrix')
def get_correlation_matrix(sport: str = 'NBA'):
    sport_stats = {
        'NBA': ['points','rebounds','assists','steals','blocks','threes','pts_reb_ast'],
        'NFL': ['passing_yards','rushing_yards','receiving_yards','receptions','passing_tds','receiving_tds'],
        'MLB': ['hits','home_runs','rbi','total_bases','strikeouts'],
        'NHL': ['goals','assists','shots','points']
    }
    stats = sport_stats.get(sport, [])
    matrix = []
    for a in stats:
        row = {'stat': a}
        for b in stats:
            row[b] = get_correlation(a, b) if a != b else 1.0
        matrix.append(row)
    return {'sport': sport, 'stats': stats, 'matrix': matrix}
