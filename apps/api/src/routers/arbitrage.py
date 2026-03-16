# apps/api/src/routers/arbitrage.py
from fastapi import APIRouter, Query, Depends
from typing import Optional
from services.props_service import get_all_props
from core.sports_config import SPORT_DISPLAY
from common_deps import get_user_tier, require_elite

router = APIRouter(tags=["arbitrage"])

def american_to_decimal(odds: int) -> float:
    if odds > 0:
        return (odds / 100) + 1
    return (100 / abs(odds)) + 1

def find_arb(over_odds: int, under_odds: int) -> Optional[dict]:
    over_dec = american_to_decimal(over_odds)
    under_dec = american_to_decimal(under_odds)
    arb_pct = (1 / over_dec) + (1 / under_dec)
    
    if arb_pct < 1.0:
        profit_pct = round((1 - arb_pct) * 100, 2)
        stake = 100
        # Correctly calculate stakes for $100 total
        over_stake = round((1 / over_dec) / arb_pct * stake, 2)
        under_stake = round(stake - over_stake, 2)
        return {
            "arb_percentage": round(arb_pct * 100, 2),
            "profit_percentage": profit_pct,
            "over_stake": over_stake,
            "under_stake": under_stake,
        }
    return None

@router.get("")
async def get_arbitrage(
    sport: Optional[str] = Query(None),
    tier: str = Depends(get_user_tier)
):
    # Tier check: Arbitrage is elite only
    if tier != "elite":
        return {
            "count": 0, 
            "opportunities": [], 
            "message": "Elite subscription required for Arbitrage Scanner",
            "tier_required": "elite"
        }

    # Grouped data from props_service
    props = await get_all_props(sport_filter=sport)

    arb_opps = []
    
    for prop in props:
        # Each prop from props_service has 'all_books' with 'over' and 'under' lists
        all_books = prop.get("all_books", {})
        overs = all_books.get("over", [])
        unders = all_books.get("under", [])
        
        if not overs or not unders:
            continue
            
        # Find best over and best under
        best_over = max(overs, key=lambda x: x["odds"])
        best_under = max(unders, key=lambda x: x["odds"])
        
        # Skip if same book (not true arb)
        if best_over["book"] == best_under["book"]:
            # If there are multiple books, try to find the next best that isn't the same
            # but for simplicity in this fallback, we'll just check if they differ.
            continue
            
        arb = find_arb(best_over["odds"], best_under["odds"])
        
        if arb:
            arb_opps.append({
                "player_name": prop["player_name"],
                "sport": prop["sport"],
                "stat_type": prop["stat_type"],
                "line": prop.get("line") or best_over["line"],
                "over_book": best_over["book"],
                "over_odds": best_over["odds"],
                "under_book": best_under["book"],
                "under_odds": best_under["odds"],
                **arb,
            })

    arb_opps.sort(key=lambda x: x["profit_percentage"], reverse=True)
    return {"count": len(arb_opps), "opportunities": arb_opps}
