from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import select
from database import SessionLocal
from models.props import PropLine, PropOdds
from datetime import datetime
from typing import List, Dict, Any

router = APIRouter(prefix="/alt-lines", tags=["alt-lines"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def calculate_ev(american_odds: int, implied_hit_rate: float = 0.55) -> float:
    """Calculates Expected Value (EV) based on odds and an implied hit rate."""
    if american_odds == 0: return 0.0
    if american_odds < 0:
        decimal = 1 + (100 / abs(american_odds))
    else:
        decimal = 1 + (american_odds / 100)
    return round((implied_hit_rate * decimal) - 1, 4)

@router.get("/ladder/{player_name}/{prop_type}")
def get_alt_lines(
    player_name: str, 
    prop_type: str, 
    standard_line: float = Query(..., description="The main consensus line"),
    db: Session = Depends(get_db)
):
    """Return all available alt lines for a player/prop sorted by line value."""
    # Fetch all prop lines for this player and stat to build the ladder
    stmt = (
        select(PropLine, PropOdds)
        .join(PropOdds, PropLine.id == PropOdds.prop_line_id)
        .where(
            PropLine.player_name == player_name,
            PropLine.stat_type == prop_type,
            PropLine.is_active == True
        )
        .order_by(PropLine.line.asc())
    )
    
    results = db.execute(stmt).all()
    
    ladder = []
    seen = set()
    for prop, odds in results:
        # Use a combination of line and sportsbook as a key to avoid duplicates
        key = (prop.line, odds.sportsbook)
        if key not in seen:
            seen.add(key)
            # Use the player's historical L10 hit rate as the implied hit rate for EV
            implied_hr = (prop.hit_rate_l10 / 100) if prop.hit_rate_l10 else 0.55
            ev = calculate_ev(odds.over_odds, implied_hr)
            
            ladder.append({
                "line": prop.line,
                "bookmaker": odds.sportsbook,
                "price": odds.over_odds,
                "ev": ev,
                "is_positive_ev": ev > 0,
                "is_base": abs(prop.line - standard_line) < 0.1
            })

    return {
        "player_name": player_name,
        "prop_type": prop_type,
        "standard_line": standard_line,
        "ladder": sorted(ladder, key=lambda x: x["line"]),
        "timestamp": datetime.utcnow().isoformat()
    }
