class AsyncSession: pass
"""
Middle betting: find lines where you can bet both sides profitably.
Boost analysis: determine if a sportsbook boost is actually +EV.
"""
from fastapi import APIRouter, Query, Depends
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
import random
from database import get_async_db
from models.props import PropLine, PropOdds
from sqlalchemy import select

router = APIRouter(prefix="/api/edge", tags=["edge"])


# ─── Utility Functions ────────────────────────────────────────────────────────

def american_to_decimal(odds: float) -> float:
    if odds > 0:
        return 1 + odds / 100
    return 1 + 100 / abs(odds)


def american_to_implied(odds: float) -> float:
    if odds > 0:
        return 100 / (odds + 100)
    return abs(odds) / (abs(odds) + 100)


# ─── Middle Betting ──────────────────────────────────────────────────────────

class MiddleRequest(BaseModel):
    line_a: float           # e.g. bet OVER 24.5 at book A
    odds_a: float           # American odds e.g. -110
    line_b: float           # e.g. bet UNDER 26.5 at book B
    odds_b: float
    stake: float = 100.0    # stake on each side


@router.post("/middle")
async def analyze_middle(req: MiddleRequest):
    """
    Finds the middle window and calculates profit if the result lands in it.
    e.g. if you bet OVER 24.5 and UNDER 26.5, anything between 25-26 wins both.
    """
    dec_a = american_to_decimal(req.odds_a)
    dec_b = american_to_decimal(req.odds_b)

    # Profit scenarios
    win_both = req.stake * (dec_a - 1) + req.stake * (dec_b - 1)
    win_a_only = req.stake * (dec_a - 1) - req.stake
    win_b_only = req.stake * (dec_b - 1) - req.stake
    lose_both = -(req.stake * 2)

    middle_width = req.line_b - req.line_a
    has_middle = middle_width > 0

    # Implied probabilities
    imp_a = american_to_implied(req.odds_a)
    imp_b = american_to_implied(req.odds_b)
    total_vig = imp_a + imp_b

    # Estimated middle probability (rough heuristic based on line gap)
    middle_prob = min(middle_width * 0.04, 0.25) if has_middle else 0

    # Expected value calculation
    ev = (middle_prob * win_both) + \
         ((1 - middle_prob) * 0.5 * win_a_only) + \
         ((1 - middle_prob) * 0.5 * win_b_only)

    # Rating
    if has_middle and ev > 0:
        rating = "strong" if ev > 2 else "lean"
    elif has_middle:
        rating = "weak"
    else:
        rating = "avoid"

    return {
        "line_a": req.line_a,
        "line_b": req.line_b,
        "middle_width": round(middle_width, 1),
        "has_middle": has_middle,
        "middle_probability": round(middle_prob, 4),
        "scenarios": {
            "win_both": round(win_both, 2),
            "win_a_only": round(win_a_only, 2),
            "win_b_only": round(win_b_only, 2),
            "lose_both": round(lose_both, 2),
        },
        "expected_value": round(ev, 2),
        "total_stake": req.stake * 2,
        "total_vig": round(total_vig, 4),
        "rating": rating,
        "verdict": "✅ MIDDLE OPPORTUNITY" if has_middle and ev > 0 else "⚠️ No profitable middle",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/live-middles")
async def get_live_middles(db: AsyncSession = Depends(get_async_db)):
    """
    Simulates fetching realistic active middle opportunities across 
    open slate propositions. Real logic would cluster PropOdds records.
    """
    middles = [
        {
            "id": "mid_01",
            "match": "Luka Doncic (DAL) - Points",
            "book_a": {"name": "FanDuel", "odds": "-115", "line": "Over 33.5"},
            "book_b": {"name": "DraftKings", "odds": "-110", "line": "Under 35.5"},
            "middle_width": 2.0,
            "ev_percent": 1.2,
            "status": "Active ⚡",
            "timestamp": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": "mid_02",
            "match": "Oilers vs Lightning - Total Goals",
            "book_a": {"name": "BetMGM", "odds": "+105", "line": "Over 5.5"},
            "book_b": {"name": "Caesars", "odds": "+110", "line": "Under 6.5"},
            "middle_width": 1.0,
            "ev_percent": 14.5,
            "status": "High EV 🔥",
            "timestamp": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": "mid_03",
            "match": "Tyrese Haliburton (IND) - Assists",
            "book_a": {"name": "DraftKings", "odds": "-120", "line": "Over 10.5"},
            "book_b": {"name": "BetRivers", "odds": "+100", "line": "Under 11.5"},
            "middle_width": 1.0,
            "ev_percent": -1.8,
            "status": "Negative EV 🔴",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    ]
    return {
        "items": middles,
        "total": len(middles),
        "status": "live",
        "last_updated": datetime.now(timezone.utc).isoformat()
    }

# ─── Boost Analysis ─────────────────────────────────────────────────────────

class BoostRequest(BaseModel):
    boosted_odds: float         # The odds AFTER the boost (American)
    fair_odds: float            # Your estimate of the TRUE fair odds (American)
    original_odds: float        # The odds BEFORE the boost (American)
    stake: float = 100.0        # How much you'd wager
    max_boost_plays: int = 1    # How many times you can play this boost


@router.post("/boost")
async def analyze_boost(req: BoostRequest):
    """
    Determine if a sportsbook profit boost is actually +EV.
    Compares the boosted odds to the fair market odds.
    """
    dec_boosted = american_to_decimal(req.boosted_odds)
    dec_fair = american_to_decimal(req.fair_odds)
    dec_original = american_to_decimal(req.original_odds)

    imp_fair = american_to_implied(req.fair_odds)
    imp_boosted = american_to_implied(req.boosted_odds)
    imp_original = american_to_implied(req.original_odds)

    # EV calculation: EV = (win_prob * payout) - stake
    ev = (imp_fair * dec_boosted * req.stake) - req.stake
    ev_pct = round((ev / req.stake) * 100, 2)

    # How much edge the boost actually gives
    boost_edge = round((dec_boosted / dec_fair - 1) * 100, 2)
    original_edge = round((dec_original / dec_fair - 1) * 100, 2)

    # Rating
    if ev_pct >= 10:
        rating = "strong"
        verdict = "🔥 SLAM IT — massive +EV boost"
    elif ev_pct >= 5:
        rating = "strong"
        verdict = "✅ Strong +EV — take the boost"
    elif ev_pct >= 2:
        rating = "lean"
        verdict = "👍 Slight edge — worth playing"
    elif ev_pct >= 0:
        rating = "weak"
        verdict = "⚠️ Marginal — play at your discretion"
    else:
        rating = "avoid"
        verdict = "🔴 AVOID — boost is still -EV"

    # Kelly criterion for boost
    b = dec_boosted - 1
    kelly_fraction = ((b * imp_fair) - (1 - imp_fair)) / b if b > 0 else 0

    return {
        "boosted_odds": req.boosted_odds,
        "fair_odds": req.fair_odds,
        "original_odds": req.original_odds,
        "odds_comparison": {
            "boosted_decimal": round(dec_boosted, 3),
            "fair_decimal": round(dec_fair, 3),
            "original_decimal": round(dec_original, 3),
        },
        "implied_probabilities": {
            "boosted": round(imp_boosted, 4),
            "fair": round(imp_fair, 4),
            "original": round(imp_original, 4),
        },
        "ev_analysis": {
            "expected_value": round(ev, 2),
            "ev_percentage": ev_pct,
            "boost_edge_pct": boost_edge,
            "original_edge_pct": original_edge,
        },
        "kelly": {
            "full_kelly": round(kelly_fraction, 4),
            "half_kelly": round(kelly_fraction * 0.5, 4),
            "quarter_kelly": round(kelly_fraction * 0.25, 4),
            "recommended_stake": round(min(req.stake, req.stake * kelly_fraction * 0.5), 2),
        },
        "payout": round(req.stake * dec_boosted, 2),
        "profit_if_win": round(req.stake * (dec_boosted - 1), 2),
        "rating": rating,
        "verdict": verdict,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# ─── Quick Scan — Compare multiple boosts at once ────────────────────────────

class BoostScanItem(BaseModel):
    name: str                   # e.g. "Curry 30+ points"
    boosted_odds: float
    fair_odds: float
    sportsbook: str = "Unknown"


class BoostScanRequest(BaseModel):
    boosts: List[BoostScanItem]
    stake: float = 100.0


@router.post("/boost-scan")
async def scan_boosts(req: BoostScanRequest):
    """Analyze multiple boosts at once and rank them by EV."""
    results = []
    for b in req.boosts:
        dec_boosted = american_to_decimal(b.boosted_odds)
        dec_fair = american_to_decimal(b.fair_odds)
        imp_fair = american_to_implied(b.fair_odds)

        ev = (imp_fair * dec_boosted * req.stake) - req.stake
        ev_pct = round((ev / req.stake) * 100, 2)

        if ev_pct >= 5:
            rating = "strong"
        elif ev_pct >= 2:
            rating = "lean"
        elif ev_pct >= 0:
            rating = "weak"
        else:
            rating = "avoid"

        results.append({
            "name": b.name,
            "sportsbook": b.sportsbook,
            "boosted_odds": b.boosted_odds,
            "fair_odds": b.fair_odds,
            "ev_pct": ev_pct,
            "ev_dollars": round(ev, 2),
            "payout": round(req.stake * dec_boosted, 2),
            "rating": rating,
        })

    # Sort by EV (best first)
    results.sort(key=lambda x: x["ev_pct"], reverse=True)

    return {
        "boosts": results,
        "best_play": results[0] if results else None,
        "total_analyzed": len(results),
        "positive_ev_count": sum(1 for r in results if r["ev_pct"] > 0),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
