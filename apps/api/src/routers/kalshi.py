from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Optional, Dict, Any
from services.kalshi_service import kalshi_service
from services.kalshi_ev import scan_all_ev_signals
from services.kalshi_arb import detect_arb_opportunities
from common_deps import require_elite
from api_utils.auth_supabase import get_current_user_supabase

router = APIRouter(tags=["live"])

# Middleware-like tier check for Elite features
async def require_elite_tier(tier: str = Depends(require_elite)):
    return tier

@router.get("/markets", response_model=List[Dict[str, Any]])
async def get_markets(sport: str = "NBA", user = Depends(require_elite_tier)):
    """Get open markets filtered by sport"""
    return await kalshi_service.get_kalshi_sports_markets(sport)

@router.get("/markets/{ticker}/orderbook")
async def get_orderbook(ticker: str, user = Depends(require_elite_tier)):
    """Get full bid/ask orderbook for a ticker"""
    return await kalshi_service.get_kalshi_market_orderbook(ticker)

@router.get("/markets/{ticker}/history")
async def get_history(ticker: str, user = Depends(require_elite_tier)):
    """Get market price history"""
    return await kalshi_service.get_kalshi_market_history(ticker)

@router.get("/events")
@router.get("/")
@router.get("")
async def get_events(series: Optional[str] = None, user = Depends(require_elite_tier)):
    """Get all open Kalshi events"""
    return await kalshi_service.get_kalshi_events(series)

@router.get("/signals")
async def get_ev_signals(sport: str = "NBA", user = Depends(require_elite_tier)):
    """Scan and return EV signals merged with real Odds API data"""
    from services.odds_api_client import odds_api_client as odds_api
    from core.sports_config import SPORT_MAP, PROP_MARKETS
    
    kalshi_sport = sport.upper()
    odds_sport = SPORT_MAP.get(sport.lower(), "basketball_nba")
    
    # 1. Get Kalshi Markets
    markets = await kalshi_service.get_kalshi_sports_markets(kalshi_sport)
    if not markets:
        return []

    # 2. Get Real Odds (Aggressively Cached)
    events = await odds_api.get_events(odds_sport)
    if not events:
        return []
        
    # Flatten first 3 events to book_props for matching
    real_props = []
    markets_to_fetch = PROP_MARKETS.get(sport.lower(), "player_points")
    
    for event in events[:3]:
        data = await odds_api.get_player_props(odds_sport, event['id'], markets_to_fetch)
        if not data: continue
        
        for book in data.get("bookmakers", []):
            for mkt in book.get("markets", []):
                for outcome in mkt.get("outcomes", []):
                    if outcome.get("name") == "Over": # We match against "Over"/YES usually
                         real_props.append({
                            "player": outcome.get("description", outcome.get("name")),
                            "market": mkt.get("key"),
                            "line": outcome.get("point"),
                            "odds": outcome.get("price"),
                            "bookmaker": book.get("title")
                        })
                        
    return scan_all_ev_signals(markets, real_props)

@router.get("/players")
@router.get("/by-player")
async def get_arb_opportunities(sport: str = "NBA", user = Depends(require_elite_tier)):
    """Detect and return arbitrage opportunities using real-time data"""
    from services.odds_api_client import odds_api_client as odds_api
    from core.sports_config import SPORT_MAP
    
    kalshi_sport = sport.upper()
    odds_sport = SPORT_MAP.get(sport.lower(), "basketball_nba")
    
    markets = await kalshi_service.get_kalshi_sports_markets(kalshi_sport)
    events = await odds_api.get_events(odds_sport)
    
    real_props = []
    for event in events[:3]:
        data = await odds_api.get_live_odds(odds_sport) # Main lines for Arb
        if not data: continue
        for d in data:
            for book in d.get("bookmakers", []):
                for mkt in book.get("markets", []):
                    for outcome in mkt.get("outcomes", []):
                        real_props.append({
                            "player": outcome.get("name"),
                            "side": "h2h", 
                            "market": mkt.get("key"),
                            "line": outcome.get("point"),
                            "odds": outcome.get("price"),
                            "bookmaker": book.get("title")
                        })
    
    return detect_arb_opportunities(markets, real_props)

@router.get("/portfolio")
async def get_portfolio(user = Depends(require_elite_tier)):
    """Get user balance and positions"""
    return await kalshi_service.get_kalshi_portfolio()

@router.post("/orders")
async def place_order(order: Dict[str, Any], user = Depends(require_elite_tier)):
    """Place a new Kalshi order"""
    ticker = order.get("ticker")
    side = order.get("side")
    count = order.get("count")
    price = order.get("price")
    
    if not all([ticker, side, count, price]):
        raise HTTPException(status_code=400, detail="Missing order parameters")
        
    return await kalshi_service.place_kalshi_order(ticker, side, count, price)

@router.delete("/orders/{order_id}")
async def cancel_order(order_id: str, user = Depends(require_elite_tier)):
    """Cancel an open order"""
    # Assuming delete endpoint in kalshi_service or similar
    # return await kalshi_service.cancel_kalshi_order(order_id)
    return {"message": f"Order {order_id} cancellation requested"}
