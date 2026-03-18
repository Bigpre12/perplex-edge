# apps/api/src/routers/intel.py
import logging
from fastapi import APIRouter, Query
from services.injury_service import injury_service
from .ev import get_top_ev
from .signals import get_signals
from .whale import whale_signals
from common_deps import get_user_tier
from fastapi import Depends

router = APIRouter(tags=["search"])
logger = logging.getLogger(__name__)

@router.get("/injuries")
async def get_intel_injuries(sport: str = Query("basketball_nba")):
    """Intel-prefixed injury report."""
    try:
        # Map sport key to short name if needed
        sport_short = sport.lower()
        # Some frontend calls might send 'all'
        if sport_short == 'all':
             sport_short = 'basketball_nba' # Default fallback
             
        injuries = await injury_service.get_injuries(sport_short)
        
        # Flatten and enrich (Logic duplicated from injuries_router for consistency)
        result = []
        if isinstance(injuries, list):
            for team in injuries:
                team_name = team.get("displayName", "Unknown Team")
                for inj in team.get("injuries", []):
                    athlete = inj.get("athlete", {})
                    player_name = athlete.get("displayName", "Unknown Player")
                    status = inj.get("status", "Unknown")
                    
                    result.append({
                        "player": player_name,
                        "team": team_name,
                        "status": status,
                        "comment": inj.get("shortComment", ""),
                        "stat_impact": "Neutral", # Placeholder
                        "source": "ESPN"
                    })
                    
        if not result:
            return {"injuries": [], "sport": sport_short, "last_updated": None}
            
        return {"injuries": result, "count": len(result), "sport": sport.upper()}
    except Exception as e:
        logger.error(f"Intel Injuries Error: {e}")
        return {"injuries": [], "sport": sport, "last_updated": None}

@router.get("/whale")
async def get_intel_whale(sport: str = Query("basketball_nba"), tier: str = Depends(get_user_tier)):
    """Intel-prefixed whale signals (alias)."""
    return await whale_signals(sport=sport, tier=tier)

@router.get("/ev-top")
async def get_intel_ev_top(
    sport: str = Query("basketball_nba"),
    min_ev: float = Query(2.0),
    limit: int = Query(10)
):
    """Intel-prefixed top EV moves."""
    return await get_top_ev(sport=sport, min_ev=min_ev, limit=limit)

@router.get("/sharp-moves")
async def get_intel_sharp_moves(sport: str = Query("basketball_nba")):
    """Intel-prefixed sharp outliers."""
    return await get_signals(sport=sport)
