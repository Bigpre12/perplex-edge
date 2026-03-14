# apps/api/src/routers/arbitrage.py
from fastapi import APIRouter, Query
from typing import Optional
from services.props_service import get_all_props
from config.sports_config import SPORT_DISPLAY

router = APIRouter(prefix="/api/arbitrage", tags=["arbitrage"])

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
async def get_arbitrage(sport: Optional[str] = Query(None)):
    props = await get_all_props(sport_filter=sport)

    # Group by player + stat_type + line
    grouped: dict = {}
    for prop in props:
        key = f"{prop['player_name']}|{prop['stat_type']}|{prop['line']}"
        if key not in grouped:
            grouped[key] = {"over": {}, "under": {}, "meta": prop}
        side = prop["pick"].lower()
        book = prop["book"]
        odds = prop["odds"]
        if side in ("over", "under"):
            if book not in grouped[key][side] or odds > grouped[key][side].get(book, -9999):
                grouped[key][side][book] = odds

    arb_opps = []
    for key, data in grouped.items():
        if not data["over"] or not data["under"]:
            continue

        # Find best over and best under across all books
        best_over_book = max(data["over"], key=data["over"].get)
        best_over_odds = data["over"][best_over_book]
        best_under_book = max(data["under"], key=data["under"].get)
        best_under_odds = data["under"][best_under_book]

        # Skip if same book (not true arb)
        if best_over_book == best_under_book:
            continue

        arb = find_arb(best_over_odds, best_under_odds)
        meta = data["meta"]

        if arb:
            arb_opps.append({
                "player_name": meta["player_name"],
                "sport": meta["sport"],
                "stat_type": meta["stat_type"],
                "line": meta["line"],
                "over_book": best_over_book,
                "over_odds": best_over_odds,
                "under_book": best_under_book,
                "under_odds": best_under_odds,
                **arb,
            })

    arb_opps.sort(key=lambda x: x["profit_percentage"], reverse=True)
    return {"count": len(arb_opps), "opportunities": arb_opps}
