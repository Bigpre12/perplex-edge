# backend/routers/hedge_router.py
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix='/api/hedge', tags=['hedge'])

def american_to_decimal(odds: int) -> float:
    return (odds / 100 + 1) if odds > 0 else (100 / abs(odds) + 1)

class HedgeRequest(BaseModel):
    original_stake: float
    original_odds: int
    hedge_odds: int
    target: str = 'guaranteed_profit'

class MiddleRequest(BaseModel):
    stake: float
    line_a: float
    odds_a: int
    line_b: float
    odds_b: int

@router.post('/calculate')
def calculate_hedge(req: HedgeRequest):
    dec_orig = american_to_decimal(req.original_odds)
    dec_hedge = american_to_decimal(req.hedge_odds)
    orig_payout = req.original_stake * dec_orig
    hedge_stake = round(orig_payout / dec_hedge, 2)
    hedge_payout = round(hedge_stake * dec_hedge, 2)
    profit_if_orig_wins = round(orig_payout - req.original_stake - hedge_stake, 2)
    profit_if_hedge_wins = round(hedge_payout - hedge_stake - req.original_stake, 2)
    guaranteed_profit = min(profit_if_orig_wins, profit_if_hedge_wins)
    total_risk = round(req.original_stake + hedge_stake, 2)
    return {
        'original_stake': req.original_stake,
        'original_odds': req.original_odds,
        'hedge_stake': hedge_stake,
        'hedge_odds': req.hedge_odds,
        'total_risk': total_risk,
        'profit_if_original_wins': profit_if_orig_wins,
        'profit_if_hedge_wins': profit_if_hedge_wins,
        'guaranteed_profit': guaranteed_profit,
        'guaranteed_roi_pct': round(guaranteed_profit / total_risk * 100, 2),
        'verdict': 'LOCK IN PROFIT' if guaranteed_profit > 0 else 'REDUCE LOSS'
    }

@router.post('/middle')
def calculate_middle(req: MiddleRequest):
    dec_a = american_to_decimal(req.odds_a)
    dec_b = american_to_decimal(req.odds_b)
    win_both = req.stake * (dec_a - 1) + req.stake * (dec_b - 1)
    win_a_only = req.stake * (dec_a - 1) - req.stake
    win_b_only = req.stake * (dec_b - 1) - req.stake
    lose_both = -(req.stake * 2)
    middle_width = round(req.line_b - req.line_a, 1)
    has_middle = middle_width > 0
    return {
        'stake_per_side': req.stake,
        'total_risk': req.stake * 2,
        'line_a': req.line_a, 'odds_a': req.odds_a,
        'line_b': req.line_b, 'odds_b': req.odds_b,
        'middle_window': f'{req.line_a}-{req.line_b}' if has_middle else 'No middle',
        'middle_width': middle_width,
        'has_middle': has_middle,
        'profit_if_middle_hits': round(win_both, 2),
        'profit_if_only_a_wins': round(win_a_only, 2),
        'profit_if_only_b_wins': round(win_b_only, 2),
        'loss_if_both_lose': round(lose_both, 2),
        'middle_grade': 'EXCELLENT' if middle_width >= 2 else 'GOOD' if middle_width >= 1 else 'SLIM'
    }
