from fastapi import APIRouter, Query
from typing import List, Optional
from core.sports_config import SPORT_MAP
from services.odds_api_client import odds_api

router = APIRouter(tags=["parlay"])

@router.get("")
@router.get("/suggestions")
async def get_parlay_suggestions(
    sport: str = "basketball_nba",
    legs: int = 3
):
    """
    Suggests high-EV parlay legs for the selected sport.
    """
    api_sport = SPORT_MAP.get(sport, sport)
    # Fetch live odds and pick the top 'legs' based on some criteria
    data = await odds_api.get_live_odds(api_sport, markets="h2h")
    
    if not data:
        return []
        
    suggestions = []
    # Simplified: Pick first N games/legs
    for event in data[:legs]:
        bookmakers = event.get("bookmakers", [])
        if not bookmakers: continue
        book = bookmakers[0]
        
        markets = book.get("markets", [])
        if not markets: continue
        market = markets[0]
        
        outcomes = market.get("outcomes", [])
        if not outcomes: continue
        outcome = outcomes[0]
        
        suggestions.append({
            "player": outcome.get("name"),
            "prop": market.get("key"),
            "line": outcome.get("point", "ML"),
            "odds": outcome.get("price"),
            "game": f"{event.get('away_team', 'Away')} @ {event.get('home_team', 'Home')}"
        })
        
    # Calculate combined odds (multiplier)
    multiplier = 1.0
    for s in suggestions:
        price = s["odds"]
        if price > 0:
            multiplier *= (price / 100 + 1)
        else:
            multiplier *= (100 / abs(price) + 1)
            
    combined_american = round((multiplier - 1) * 100) if multiplier >= 2 else round(-100 / (multiplier - 1))
    
    return {
        "legs": suggestions,
        "combined_odds": f"+{combined_american}" if combined_american > 0 else str(combined_american),
        "payout_estimate_100": round(100 * multiplier, 2)
    }

@router.get("/history")
async def get_parlay_history():
    """
    Returns historical parlays for the current user.
    Placeholder: In production this queries the 'parlays' table.
    """
    return {
        "count": 0,
        "parlays": [],
        "status": "Syncing history from neural engine..."
    }
