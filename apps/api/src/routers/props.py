import logging
import os
import httpx
from fastapi import APIRouter, Query, Depends, HTTPException
from typing import Optional, List
from models.props import PropLine, PropOdds, GameLine, GameLineOdds
from models.analytical import WhaleMove
from services.props_service import get_all_props, get_team_props
from config.sports_config import SPORT_DISPLAY, ALL_SPORTS, SPORT_MAP
from common_deps import get_current_user_supabase, get_user_tier
from services.brain_service import brain_service

logger = logging.getLogger(__name__)
router = APIRouter(tags=["props"])

@router.get("")
async def player_props(
    sport: Optional[str] = Query(None),
    limit: Optional[int] = Query(None, description="Limit results"),
    tier: str = Depends(get_user_tier)
):
    # Normalize "all" to default for free tier
    if sport == "all" or not sport:
        sport = "basketball_nba"

    # 🔓 LOCK REMOVAL: Tier-Gating bypass in dev mode
    from config import settings
    if tier == "free" and sport != "basketball_nba" and not settings.DEVELOPMENT_MODE:
        raise HTTPException(status_code=403, detail="Upgrade to Pro to access all sports")

    try:
        logger.info(f"Fetching player props for sport: {sport}")
        
        # Use props_service which now has robust fallback to mock data
        from services.props_service import props_service
        final_props = await props_service.get_all_props(sport_filter=sport)
        
        if not final_props:
            return {"count": 0, "props": [], "source": "empty_results"}

        # 🔓 LOCK REMOVAL: Bypass volume limit in dev mode
        if tier == "free" and not settings.DEVELOPMENT_MODE:
            final_props = final_props[:5]
        
        # Add ID and missing fields for frontend if needed (enrichment)
        # props_service.get_all_props returning a list of dicts.
        # Ensure it matches the expected structure.
        
        # 🧠 Enrich with Advisor Intelligence (if not already enriched)
        # props_service.get_all_props already calls score_and_recommend for DB fallback, 
        # but let's ensure consistency here if we want brain scoring.
        final_props = await brain_service.score_and_recommend(final_props)
            
        return {
            "count": len(final_props), 
            "props": final_props[:limit] if limit else final_props, 
            "source": "props_service"
        }
        
    except Exception as e:
        logger.error(f"Error in player_props router: {str(e)}", exc_info=True)
        return {"count": 0, "props": [], "error": "Internal server error"}
        
    except Exception as e:
        logger.error(f"Error in player_props router: {str(e)}", exc_info=True)
        return {"count": 0, "props": [], "error": "Internal server error"}

@router.get("/player")
async def get_player_props_v2(sport: str = "basketball_nba", bookmaker: str = "fanduel"):
    """Refactored to use OddsApiClient (Cached & Gated)"""
    try:
        from app.services.odds_api_client import odds_api
        from config.sports_config import SPORT_MAP, PROP_MARKETS
        
        odds_key = SPORT_MAP.get(sport, sport)
        markets = PROP_MARKETS.get(sport, "player_points")

        # Step 1: Get today's events (CACHED)
        events = await odds_api.get_events(odds_key)
        if not events:
            return {"data": [], "message": "No events today or API exhausted"}

        # Step 2: Get props for first 2 events (CACHED)
        # 🔓 LOCK REMOVAL: Increase event limit in dev mode
        from config import settings
        event_limit = len(events) if settings.DEVELOPMENT_MODE else 2
        for event in events[:event_limit]:
            try:
                data = await odds_api.get_player_props(odds_key, event['id'], markets)
                if not data:
                    continue
                
                game_label = f"{event.get('away_team')} @ {event.get('home_team')}"
                
                # Check for the requested bookmaker specifically, or take first available
                bookmakers = data.get("bookmakers", [])
                target_book = next((b for b in bookmakers if b['key'] == bookmaker), None)
                if not target_book and bookmakers:
                    target_book = bookmakers[0]
                
                if not target_book:
                    continue

                for market in target_book.get("markets", []):
                    for outcome in market.get("outcomes", []):
                        if outcome.get("name") not in ["Over", "Under"]:
                            continue
                        all_props.append({
                            "player": outcome.get("description", outcome.get("name")),
                            "stat_type": market.get("key", "").replace("player_", "").replace("_", " ").title(),
                            "market_key": market.get("key"),
                            "line": outcome.get("point", 0),
                            "side": outcome.get("name"),
                            "odds": outcome.get("price"),
                            "sportsbook": target_book.get("title"),
                            "game": game_label,
                            "game_id": event.get("id"),
                            "commence_time": event.get("commence_time"),
                            "sport": sport
                        })
            except Exception as inner_e:
                logger.error(f"Error fetching props for event {event.get('id')}: {inner_e}")
                continue

        return {"data": all_props, "count": len(all_props), "source": "cached_odds_api"}

    except Exception as e:
        logger.error(f"Error in get_player_props_v2: {e}")
        return {"data": [], "error": str(e)}

@router.get("/books/available")
async def get_available_books(sport: str = Query("basketball_nba")):
    """Pull ALL available books from Odds API"""
    try:
        from app.services.odds_api_client import odds_api
        api_sport = SPORT_MAP.get(sport, sport)
        # Fetch odds to see which bookmakers are available
        data = await odds_api.get_live_odds(api_sport, regions="us,us2,eu,uk", markets="h2h")
        
        unique_books = {}
        for event in data:
            for book in event.get("bookmakers", []):
                unique_books[book["key"]] = book["title"]
        
        return [{"key": k, "name": v} for k, v in unique_books.items()]
    except Exception as e:
        logger.error(f"Error fetching available books: {e}")
        return []


@router.get("/best")
async def get_best_value_props(sport: str = "basketball_nba"):
    """Fetch props with significantly high edge/EV."""
    try:
        props = await get_all_props(sport_filter=sport)
        # Score and recommend uses the brain_service to rank them
        scored = await brain_service.score_and_recommend(props)
        # Filter for "Elite" or "Good" marks
        best = [p for p in scored if p.get("grade") in ["S", "A", "Elite", "High Value"]]
        return {"count": len(best), "props": best[:20], "source": "brain_filter"}
    except Exception as e:
        logger.error(f"Error in get_best_value_props: {e}")
        return {"count": 0, "props": [], "error": str(e)}

@router.get("/team")
async def team_props(sport: Optional[str] = Query(None)):
    try:
        logger.info(f"Fetching team props for sport: {sport}")
        games = await get_team_props(sport_filter=sport)
        return {"count": len(games), "games": games}
    except Exception as e:
        logger.error(f"Error fetching team props for {sport}: {str(e)}", exc_info=True)
        return {"count": 0, "games": [], "error": "Internal server error"}

@router.get("/scored")
async def get_scored_props_count(sport: str = "basketball_nba"):
    """Return the count of props currently scored by the engine."""
    try:
        props = await get_all_props(sport_filter=sport)
        scored = await brain_service.score_and_recommend(props)
        count = len([p for p in scored if p.get("recommendation")])
        return {"count": count, "sport": sport, "timestamp": datetime.now(timezone.utc).isoformat()}
    except Exception as e:
        logger.error(f"Error in get_scored_props_count: {e}")
        return {"count": 0, "error": str(e)}

@router.get("/sports")
async def list_sports():
    return {
        "sports": [
            {"key": k, "display": v}
            for k, v in SPORT_DISPLAY.items()
        ]
    }

@router.get("/players/{player_name}")
async def get_player_profile(
    player_name: str,
    user: dict = Depends(get_current_user_supabase)
):
    """Exposes highly detailed player profile with historical hit rates."""
    from urllib.parse import unquote
    from database import get_db_connection
    from services.ev_service import grade_prop

    name = unquote(player_name)
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Hit rates
        cursor.execute("""
            SELECT stat_type,
                   ROUND(AVG(CASE WHEN hit = 1 THEN 100.0 ELSE 0 END), 1) as hit_rate,
                   COUNT(*) as total_picks,
                   SUM(CASE WHEN hit = 1 THEN 1 ELSE 0 END) as hits
            FROM picks
            WHERE player_name = ? AND user_id = ? AND hit IS NOT NULL
            GROUP BY stat_type
            ORDER BY total_picks DESC
        """, (name, user["id"]))
        hit_rates = [dict(r) for r in cursor.fetchall()]

        # Recent stats
        cursor.execute("""
            SELECT game_time as game_date, opponent, stat_type, actual_value as value
            FROM picks
            WHERE player_name = ? AND user_id = ? AND actual_value IS NOT NULL
            ORDER BY game_time DESC LIMIT 20
        """, (name, user["id"]))
        stats = [dict(r) for r in cursor.fetchall()]

        # Get meta
        cursor.execute("SELECT sport, team FROM picks WHERE player_name = ? AND user_id = ? ORDER BY game_time DESC LIMIT 1", (name, user["id"]))
        meta = cursor.fetchone()
        
        # Today's live props
        props = await get_all_props()
        player_props = [p for p in props if p["player_name"].lower() == name.lower()]
        
        return {
            "player_name": name,
            "team": meta["team"] if meta else "N/A",
            "sport": meta["sport"] if meta else "NBA",
            "hit_rates": hit_rates,
            "stats": stats,
            "props": player_props
        }
    finally:
        conn.close()
