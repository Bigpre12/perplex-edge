"""Stats API endpoints for hit rate tracking and player performance."""

from typing import Optional, Annotated
from datetime import datetime

from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel, PlainSerializer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.results_tracker import ResultsTracker
from app.services.hot_cold_service import get_hot_players_with_best_market, get_hot_cold_players_by_market
from app.models import Sport


router = APIRouter()


# =============================================================================
# Schemas
# =============================================================================

def serialize_datetime_utc(dt: datetime) -> str:
    """Serialize datetime to ISO format with Z suffix for UTC."""
    if dt is None:
        return None
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


UTCDatetime = Annotated[datetime, PlainSerializer(serialize_datetime_utc)]


def compute_trust_tag(total_picks: int, hit_rate_7d: float, current_streak: int) -> str:
    """
    Compute a trust score tag based on sample size and performance.
    
    Tags:
    - "strong": High hit rate + positive streak + good sample size
    - "ok": Decent performance
    - "thin": Small sample size
    - "weak": Poor performance despite sample size
    """
    if total_picks < 5:
        return "thin"
    if hit_rate_7d >= 0.70 and current_streak >= 2:
        return "strong"
    if hit_rate_7d >= 0.55:
        return "ok"
    return "weak"


class HotPlayer(BaseModel):
    """Hot player response."""
    player_id: int
    player_name: str
    hit_rate_7d: float
    total_7d: int
    hits_7d: int
    current_streak: int
    last_5: Optional[str] = None
    # Market-specific fields (populated when include_market=true)
    stat_type: Optional[str] = None  # e.g., "PTS", "REB", "3PM"
    side: Optional[str] = None  # "over" or "under"
    # Trust tag for quality assessment
    trust_tag: Optional[str] = None  # "strong", "ok", "thin", "weak"


class HotPlayerList(BaseModel):
    """List of hot players."""
    items: list[HotPlayer]
    total: int


class StreakPlayer(BaseModel):
    """Player on a streak, tied to a specific stat type and direction."""
    player_id: int
    player_name: str
    streak: int
    stat_type: Optional[str] = None
    direction: Optional[str] = None
    hit_rate_7d: Optional[float] = None
    last_5: Optional[str] = None


class StreaksList(BaseModel):
    """Hot and cold streaks."""
    hot: list[StreakPlayer]
    cold: list[StreakPlayer]


class RecentResult(BaseModel):
    """Recent pick result."""
    result_id: int
    player_id: int
    player_name: str
    stat_type: Optional[str] = None
    line: float
    side: str
    actual_value: float
    hit: bool
    settled_at: str
    game_id: int


class RecentResultList(BaseModel):
    """List of recent results."""
    items: list[RecentResult]
    total: int


class PlayerStats(BaseModel):
    """Player stats summary."""
    hit_rate_7d: Optional[float] = None
    total_7d: int = 0
    hit_rate_all: Optional[float] = None
    total_all: int = 0
    current_streak: int = 0
    best_streak: int = 0
    worst_streak: int = 0
    last_5: Optional[str] = None


class PlayerResult(BaseModel):
    """Individual player result."""
    stat_type: Optional[str] = None
    line: float
    side: str
    actual_value: float
    hit: bool
    settled_at: str


class PlayerHistory(BaseModel):
    """Player history response."""
    player_id: int
    player_name: str
    stats: PlayerStats
    results: list[PlayerResult]


class SettleResponse(BaseModel):
    """Pick settlement response."""
    game_id: int
    settled: int
    hits: int
    misses: int
    hit_rate: float = 0


# =============================================================================
# Endpoints
# =============================================================================

@router.get("/sports/{sport_id}/hot-players", response_model=HotPlayerList, tags=["stats"])
async def get_hot_players(
    sport_id: int,
    min_picks: int = Query(5, ge=1, description="Minimum picks in last 7 days"),
    limit: int = Query(10, ge=1, le=50, description="Maximum players to return"),
    include_market: bool = Query(False, description="Include best market (stat_type + side) per player"),
    market: Optional[str] = Query(None, description="Filter by market (PTS, REB, AST, 3PM, etc.)"),
    side: Optional[str] = Query(None, description="Filter by side (over/under)"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get players with the best 7-day hit rates.
    
    Returns top performers by recent hit rate, useful for identifying
    hot players to follow.
    
    When include_market=true, returns each player's best-performing market
    (stat_type like PTS, REB, 3PM and side like over/under).
    
    When market or side is specified, filters to that specific market/side
    using PlayerMarketHitRate data.
    """
    # Verify sport exists
    sport = await db.get(Sport, sport_id)
    if not sport:
        raise HTTPException(status_code=404, detail=f"Sport {sport_id} not found")
    
    # If market or side filter is specified, use market-specific query
    if market or side:
        result = await get_hot_cold_players_by_market(
            db, sport_id=sport_id, market=market, side=side, min_picks=min_picks, limit=limit
        )
        hot_players = [
            {
                "player_id": p.get("player_id", 0),
                "player_name": p.get("player_name", ""),
                "hit_rate_7d": p.get("hit_rate_7d", 0.0),
                "total_7d": p.get("total_7d", 0),
                "hits_7d": p.get("hits_7d", 0),
                "current_streak": p.get("current_streak", 0),
                "last_5": p.get("last_5_results"),
                "stat_type": p.get("market", ""),
                "side": p.get("side"),
                "trust_tag": compute_trust_tag(p.get("total_7d", 0), p.get("hit_rate_7d", 0.0), p.get("current_streak", 0)),
            }
            for p in result.get("hot", [])
        ]
    elif include_market:
        # Use market-aware function that returns best market per player
        hot_players = await get_hot_players_with_best_market(
            db, sport_id, min_picks=min_picks, limit=limit
        )
        # Add trust_tag to each player
        hot_players = [
            {**p, "trust_tag": compute_trust_tag(p.get("total_7d", 0), p.get("hit_rate_7d", 0.0), p.get("current_streak", 0))}
            for p in hot_players
        ]
    else:
        # Use original aggregated function
        tracker = ResultsTracker()
        hot_players = await tracker.get_hot_players(db, sport_id, min_picks, limit)
        # Add trust_tag to each player
        hot_players = [
            {**p, "trust_tag": compute_trust_tag(p.get("total_7d", 0), p.get("hit_rate_7d", 0.0), p.get("current_streak", 0))}
            for p in hot_players
        ]
    
    return HotPlayerList(
        items=[HotPlayer(**p) for p in hot_players],
        total=len(hot_players),
    )


@router.get("/sports/{sport_id}/cold-players", response_model=HotPlayerList, tags=["stats"])
async def get_cold_players(
    sport_id: int,
    min_picks: int = Query(5, ge=1, description="Minimum picks in last 7 days"),
    limit: int = Query(10, ge=1, le=50, description="Maximum players to return"),
    market: Optional[str] = Query(None, description="Filter by market (PTS, REB, AST, 3PM, etc.)"),
    side: Optional[str] = Query(None, description="Filter by side (over/under)"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get players with the worst 7-day hit rates.
    
    Returns players who have been cold recently, useful for fading.
    
    When market or side is specified, filters to that specific market/side
    using PlayerMarketHitRate data.
    """
    # Verify sport exists
    sport = await db.get(Sport, sport_id)
    if not sport:
        raise HTTPException(status_code=404, detail=f"Sport {sport_id} not found")
    
    # If market or side filter is specified, use market-specific query
    if market or side:
        result = await get_hot_cold_players_by_market(
            db, sport_id=sport_id, market=market, side=side, min_picks=min_picks, limit=limit
        )
        cold_players = [
            {
                "player_id": p.get("player_id", 0),
                "player_name": p.get("player_name", ""),
                "hit_rate_7d": p.get("hit_rate_7d", 0.0),
                "total_7d": p.get("total_7d", 0),
                "hits_7d": p.get("hits_7d", 0),
                "current_streak": p.get("current_streak", 0),
                "last_5": p.get("last_5_results"),
                "stat_type": p.get("market", ""),
                "side": p.get("side"),
                "trust_tag": compute_trust_tag(p.get("total_7d", 0), p.get("hit_rate_7d", 0.0), p.get("current_streak", 0)),
            }
            for p in result.get("cold", [])
        ]
    else:
        tracker = ResultsTracker()
        cold_players = await tracker.get_cold_players(db, sport_id, min_picks, limit)
        # Add trust_tag to each player
        cold_players = [
            {**p, "trust_tag": compute_trust_tag(p.get("total_7d", 0), p.get("hit_rate_7d", 0.0), p.get("current_streak", 0))}
            for p in cold_players
        ]
    
    return HotPlayerList(
        items=[HotPlayer(**p) for p in cold_players],
        total=len(cold_players),
    )


@router.get("/sports/{sport_id}/streaks", response_model=StreaksList, tags=["stats"])
async def get_streaks(
    sport_id: int,
    min_streak: int = Query(3, ge=2, description="Minimum streak length"),
    limit: int = Query(20, ge=1, le=50, description="Maximum players per category"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get players on hot and cold streaks.
    
    Returns players currently on winning or losing streaks.
    """
    # Verify sport exists
    sport = await db.get(Sport, sport_id)
    if not sport:
        raise HTTPException(status_code=404, detail=f"Sport {sport_id} not found")
    
    tracker = ResultsTracker()
    streaks = await tracker.get_streaks(db, sport_id, min_streak, limit)
    
    return StreaksList(
        hot=[StreakPlayer(**p) for p in streaks["hot"]],
        cold=[StreakPlayer(**p) for p in streaks["cold"]],
    )


@router.get("/sports/{sport_id}/recent-results", response_model=RecentResultList, tags=["stats"])
async def get_recent_results(
    sport_id: int,
    limit: int = Query(20, ge=1, le=100, description="Maximum results to return"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get the most recent pick results.
    
    Returns a feed of recently settled picks showing hits and misses.
    """
    # Verify sport exists
    sport = await db.get(Sport, sport_id)
    if not sport:
        raise HTTPException(status_code=404, detail=f"Sport {sport_id} not found")
    
    tracker = ResultsTracker()
    results = await tracker.get_recent_results(db, sport_id, limit)
    
    return RecentResultList(
        items=[RecentResult(**r) for r in results],
        total=len(results),
    )


@router.get("/players/{player_id}/history", response_model=PlayerHistory, tags=["stats"])
async def get_player_history(
    player_id: int,
    limit: int = Query(50, ge=1, le=200, description="Maximum results to return"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get detailed pick history for a specific player.
    
    Returns overall stats and recent results for the player.
    """
    tracker = ResultsTracker()
    history = await tracker.get_player_history(db, player_id, limit)
    
    if "error" in history:
        raise HTTPException(status_code=404, detail=history["error"])
    
    return PlayerHistory(
        player_id=history["player_id"],
        player_name=history["player_name"],
        stats=PlayerStats(**history["stats"]),
        results=[PlayerResult(**r) for r in history["results"]],
    )


@router.post("/games/{game_id}/settle", response_model=SettleResponse, tags=["stats"])
async def settle_game_picks(
    game_id: int,
    simulate: bool = Query(False, description="Simulate results for testing"),
    db: AsyncSession = Depends(get_db),
):
    """
    Settle all picks for a completed game.
    
    Compares actual player stats against pick lines to determine hits/misses.
    Use simulate=true to generate fake stats for testing.
    """
    tracker = ResultsTracker()
    
    if simulate:
        result = await tracker.simulate_game_results(db, game_id)
    else:
        result = await tracker.settle_picks_for_game(db, game_id)
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return SettleResponse(
        game_id=result.get("game_id", game_id),
        settled=result.get("settled", 0),
        hits=result.get("hits", 0),
        misses=result.get("misses", 0),
        hit_rate=result.get("hit_rate", 0),
    )


@router.post("/games/{game_id}/simulate", response_model=SettleResponse, tags=["stats"])
async def simulate_game_results(
    game_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Simulate game results for testing.
    
    Creates fake player stats and settles picks based on simulated outcomes.
    Useful for testing the hit rate tracking system.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        tracker = ResultsTracker()
        result = await tracker.simulate_game_results(db, game_id)
        
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        
        return SettleResponse(
            game_id=result.get("game_id", game_id),
            settled=result.get("settled", 0),
            hits=result.get("hits", 0),
            misses=result.get("misses", 0),
            hit_rate=result.get("hit_rate", 0),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error simulating game {game_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Simulation failed: {str(e)[:200]}")
