from fastapi import APIRouter
from app.services.odds_api_client import odds_api

router = APIRouter(tags=["sharp_money"])

@router.get("/sharp-money")
async def get_sharp_money_signals(sport: str = "basketball_nba"):
    from config.sports_config import SPORT_MAP
    api_sport = SPORT_MAP.get(sport, sport)
    """
    Detects sharp money signals. Fallback: use player props discrepancies from PropsService.
    """
    SHARP_BOOKS = {"pinnacle", "betcris", "circa", "bookmaker"}
    SQUARE_BOOKS = {"draftkings", "fanduel", "betmgm", "caesars", "pointsbet"}

    # 1. Try Game Odds first
    data = await odds_api.get_live_odds(api_sport, regions="us,eu", markets="h2h,spreads")
    signals = []

    if data:
        for event in data:
            sharp_odds: dict[str, list] = {}
            square_odds: dict[str, list] = {}
            for book in event.get("bookmakers", []):
                bk = book["key"]
                for mkt in book.get("markets", []):
                    for outcome in mkt.get("outcomes", []):
                        key = f"{mkt['key']}_{outcome['name']}"
                        price = outcome.get("price", 0)
                        if bk in SHARP_BOOKS:
                            sharp_odds.setdefault(key, []).append(price)
                        elif bk in SQUARE_BOOKS:
                            square_odds.setdefault(key, []).append(price)

            for key in sharp_odds:
                if key not in square_odds: continue
                s_avg = sum(sharp_odds[key]) / len(sharp_odds[key])
                sq_avg = sum(square_odds[key]) / len(square_odds[key])
                delta = s_avg - sq_avg
                if abs(delta) >= 5:
                    market_key, team = key.split("_", 1)
                    signals.append({
                        "game": f"{event['away_team']} @ {event['home_team']}",
                        "sport": sport,
                        "commence_time": event.get("commence_time"),
                        "team": team,
                        "market": market_key,
                        "sharp_avg_odds": round(s_avg, 1),
                        "square_avg_odds": round(sq_avg, 1),
                        "delta": round(delta, 1),
                        "signal": "SHARP_OVER" if delta > 0 else "SHARP_UNDER",
                        "strength": "STRONG" if abs(delta) >= 10 else "MODERATE"
                    })

    # 2. Fallback: Player Prop Sharp Indicators
    if not signals:
        from services.props_service import props_service
        raw_props = await props_service.get_all_props(sport_filter=sport)
        for p in raw_props:
            all_books = p.get("all_books", {})
            ov = all_books.get("over", [])
            
            # Detect sharp book outlier in props
            sharp_prices = [b["odds"] for b in ov if b["book_key"] in SHARP_BOOKS]
            square_prices = [b["odds"] for b in ov if b["book_key"] in SQUARE_BOOKS]
            
            if sharp_prices and square_prices:
                s_avg = sum(sharp_prices) / len(sharp_prices)
                sq_avg = sum(square_prices) / len(square_prices)
                delta = s_avg - sq_avg
                
                if abs(delta) >= 8: # Higher threshold for props
                    signals.append({
                        "game": f"{p['player_name']} ({p['stat_type']})",
                        "sport": sport,
                        "commence_time": p.get("commence_time"),
                        "team": p["player_name"],
                        "market": p["stat_type"],
                        "sharp_avg_odds": round(s_avg, 1),
                        "square_avg_odds": round(sq_avg, 1),
                        "delta": round(delta, 1),
                        "signal": "SHARP_PROP_MOVE",
                        "strength": "MODERATE"
                    })

    signals.sort(key=lambda x: abs(x["delta"]), reverse=True)
    return {"signals": signals[:20], "count": len(signals)}
@router.get("/alerts")
async def get_alerts(sport: str = "all"):
    """
    Returns recent sharp money alerts to populate notification center.
    """
    # Simply reuse the sharp-money signal logic but return in an alerts-friendly format
    res = await get_sharp_money_signals(sport if sport != "all" else "basketball_nba")
    signals = res.get("signals", [])
    
    alerts = []
    for s in signals[:10]:
        alerts.append({
            "id": f"alert-{s.get('team')}-{s.get('market')}",
            "type": "SHARP_MONEY",
            "title": f"Sharp Money: {s['team']}",
            "message": f"Heavy {s['signal']} detected on {s['market']} ({s['delta']} point delta).",
            "severity": "high" if s['strength'] == "STRONG" else "medium",
            "timestamp": s.get("commence_time") or datetime.now(timezone.utc).isoformat(),
            "meta": s
        })
        
    return {
        "items": alerts,
        "total": len(alerts),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

from datetime import datetime, timezone
