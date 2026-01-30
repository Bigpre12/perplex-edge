"""Model Picks API endpoints."""

import logging
from typing import Optional
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models import ModelPick, Game, Sport, Market, Player
from app.schemas.model_pick import ModelPickList, ModelPickWithDetails, PickSummary
from app.services.picks_generator import generate_picks

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/debug/config")
async def debug_config():
    """Debug endpoint to check current configuration values."""
    from app.core.config import get_settings
    settings = get_settings()
    return {
        "scheduler_use_stubs": settings.scheduler_use_stubs,
        "scheduler_enabled": settings.scheduler_enabled,
        "odds_api_key_set": bool(settings.odds_api_key),
        "odds_api_key_preview": settings.odds_api_key[:8] + "..." if settings.odds_api_key else None,
        "environment": settings.environment,
    }


# Sport key mappings for refresh endpoint
SPORT_KEY_MAP = {
    "nba": "basketball_nba",
    "nfl": "americanfootball_nfl",
    "mlb": "baseball_mlb",
    "nhl": "icehockey_nhl",
}


@router.get("", response_model=ModelPickList)
async def list_picks(
    sport: Optional[str] = Query(None, description="Filter by sport"),
    game_id: Optional[int] = Query(None, description="Filter by game"),
    active_only: bool = Query(True, description="Only show active picks"),
    min_confidence: float = Query(0.0, description="Minimum confidence score"),
    min_ev: float = Query(0.0, description="Minimum expected value"),
    limit: int = Query(50, le=200),
    offset: int = Query(0),
    db: AsyncSession = Depends(get_db),
):
    """List model picks with optional filters."""
    query = (
        select(ModelPick)
        .options(
            selectinload(ModelPick.sport),
            selectinload(ModelPick.game).selectinload(Game.home_team),
            selectinload(ModelPick.game).selectinload(Game.away_team),
            selectinload(ModelPick.market),
            selectinload(ModelPick.player),
        )
        .order_by(ModelPick.confidence_score.desc())
    )

    if sport:
        query = query.join(Sport).where(Sport.league_code.ilike(f"%{sport}%"))
    
    if game_id:
        query = query.where(ModelPick.game_id == game_id)
    
    if active_only:
        query = query.where(ModelPick.is_active == True)
    
    if min_confidence > 0:
        query = query.where(ModelPick.confidence_score >= min_confidence)
    
    if min_ev > 0:
        query = query.where(ModelPick.expected_value >= min_ev)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)

    # Get paginated results
    query = query.limit(limit).offset(offset)
    result = await db.execute(query)
    picks = result.scalars().all()

    # Build response with details
    items = []
    for pick in picks:
        game = pick.game
        market = pick.market
        player = pick.player
        sport_obj = pick.sport

        items.append(ModelPickWithDetails(
            id=pick.id,
            sport_id=pick.sport_id,
            game_id=pick.game_id,
            player_id=pick.player_id,
            market_id=pick.market_id,
            side=pick.side,
            line_value=pick.line_value,
            odds=pick.odds,
            model_probability=pick.model_probability,
            implied_probability=pick.implied_probability,
            expected_value=pick.expected_value,
            hit_rate_30d=pick.hit_rate_30d,
            hit_rate_10g=pick.hit_rate_10g,
            confidence_score=pick.confidence_score,
            is_active=pick.is_active,
            generated_at=pick.generated_at,
            sport_name=sport_obj.name if sport_obj else "Unknown",
            market_type=market.market_type if market else "unknown",
            stat_type=market.stat_type if market else None,
            player_name=player.name if player else None,
            home_team=game.home_team.name if game and game.home_team else "Unknown",
            away_team=game.away_team.name if game and game.away_team else "Unknown",
            game_time=game.start_time if game else datetime.utcnow(),
        ))

    return ModelPickList(items=items, total=total or 0)


@router.get("/top", response_model=ModelPickList)
async def get_top_picks(
    sport: Optional[str] = Query(None, description="Filter by sport"),
    limit: int = Query(10, le=50),
    db: AsyncSession = Depends(get_db),
):
    """Get top picks by expected value for today's games."""
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow = today + timedelta(days=1)

    query = (
        select(ModelPick)
        .options(
            selectinload(ModelPick.sport),
            selectinload(ModelPick.game).selectinload(Game.home_team),
            selectinload(ModelPick.game).selectinload(Game.away_team),
            selectinload(ModelPick.market),
            selectinload(ModelPick.player),
        )
        .join(Game)
        .where(
            ModelPick.is_active == True,
            Game.start_time >= today,
            Game.start_time < tomorrow,
        )
        .order_by(ModelPick.expected_value.desc())
        .limit(limit)
    )

    if sport:
        query = query.join(Sport).where(Sport.league_code.ilike(f"%{sport}%"))

    result = await db.execute(query)
    picks = result.scalars().all()

    items = []
    for pick in picks:
        game = pick.game
        market = pick.market
        player = pick.player
        sport_obj = pick.sport

        items.append(ModelPickWithDetails(
            id=pick.id,
            sport_id=pick.sport_id,
            game_id=pick.game_id,
            player_id=pick.player_id,
            market_id=pick.market_id,
            side=pick.side,
            line_value=pick.line_value,
            odds=pick.odds,
            model_probability=pick.model_probability,
            implied_probability=pick.implied_probability,
            expected_value=pick.expected_value,
            hit_rate_30d=pick.hit_rate_30d,
            hit_rate_10g=pick.hit_rate_10g,
            confidence_score=pick.confidence_score,
            is_active=pick.is_active,
            generated_at=pick.generated_at,
            sport_name=sport_obj.name if sport_obj else "Unknown",
            market_type=market.market_type if market else "unknown",
            stat_type=market.stat_type if market else None,
            player_name=player.name if player else None,
            home_team=game.home_team.name if game and game.home_team else "Unknown",
            away_team=game.away_team.name if game and game.away_team else "Unknown",
            game_time=game.start_time if game else datetime.utcnow(),
        ))

    return ModelPickList(items=items, total=len(items))


@router.get("/summary", response_model=PickSummary)
async def get_picks_summary(
    sport: Optional[str] = Query(None, description="Filter by sport"),
    db: AsyncSession = Depends(get_db),
):
    """Get summary statistics for model picks."""
    base_query = select(ModelPick)
    
    if sport:
        base_query = base_query.join(Sport).where(Sport.league_code.ilike(f"%{sport}%"))

    # Total picks
    total_result = await db.execute(
        select(func.count()).select_from(base_query.subquery())
    )
    total_picks = total_result.scalar() or 0

    # Active picks
    active_result = await db.execute(
        select(func.count()).select_from(
            base_query.where(ModelPick.is_active == True).subquery()
        )
    )
    active_picks = active_result.scalar() or 0

    # Average EV
    avg_ev_result = await db.execute(
        select(func.avg(ModelPick.expected_value)).select_from(
            base_query.where(ModelPick.is_active == True).subquery()
        )
    )
    avg_ev = avg_ev_result.scalar() or 0.0

    # Average confidence
    avg_conf_result = await db.execute(
        select(func.avg(ModelPick.confidence_score)).select_from(
            base_query.where(ModelPick.is_active == True).subquery()
        )
    )
    avg_confidence = avg_conf_result.scalar() or 0.0

    # High confidence picks (> 0.7)
    high_conf_result = await db.execute(
        select(func.count()).select_from(
            base_query.where(
                ModelPick.is_active == True,
                ModelPick.confidence_score > 0.7,
            ).subquery()
        )
    )
    high_confidence_picks = high_conf_result.scalar() or 0

    return PickSummary(
        total_picks=total_picks,
        active_picks=active_picks,
        avg_ev=round(avg_ev, 4),
        avg_confidence=round(avg_confidence, 4),
        high_confidence_picks=high_confidence_picks,
    )


@router.post("/refresh")
async def refresh_picks(
    sport: str = Query("nba", description="Sport to refresh: nba, nfl, mlb, nhl"),
    db: AsyncSession = Depends(get_db),
):
    """
    Full refresh: sync new data, clear old games, generate picks.
    
    This endpoint performs a SAFE data refresh for a sport:
    1. Tries to sync from real Odds API first
    2. Falls back to stub data if API fails (rate limit, errors, etc.)
    3. Only clears old data AFTER new data is confirmed
    4. Generates model picks
    
    This prevents data loss when the API is unavailable.
    """
    from app.services.etl_games_and_lines import clear_stale_games, sync_games_and_lines
    from app.core.config import get_settings
    
    settings = get_settings()
    prefer_stubs = settings.scheduler_use_stubs
    
    try:
        sport_key = SPORT_KEY_MAP.get(sport.lower())
        if not sport_key:
            raise HTTPException(status_code=400, detail=f"Unknown sport: {sport}")
        
        sync_stats = None
        used_stubs = prefer_stubs
        clear_stats = {"skipped": True, "reason": "no_new_data"}
        
        # =================================================================
        # Step 1: Try to sync data (API first if not preferring stubs)
        # =================================================================
        if not prefer_stubs:
            # Try real API first
            logger.info(f"Trying real API for {sport_key}...")
            try:
                sync_stats = await sync_games_and_lines(
                    db, sport_key, include_props=True, use_stubs=False
                )
                
                # Check if API returned useful data
                has_errors = len(sync_stats.get("errors", [])) > 0
                has_games = sync_stats.get("games_created", 0) > 0 or sync_stats.get("games_updated", 0) > 0
                has_props = sync_stats.get("props_added", 0) > 0
                
                if has_errors and not has_props:
                    logger.warning(f"API had errors and no props, falling back to stubs: {sync_stats.get('errors', [])[:3]}")
                    sync_stats = None  # Will trigger fallback
                elif not has_games and not has_props:
                    logger.warning("API returned no data, falling back to stubs")
                    sync_stats = None  # Will trigger fallback
                else:
                    logger.info(f"API sync successful: {sync_stats}")
                    used_stubs = False
            except Exception as e:
                logger.warning(f"API sync failed, falling back to stubs: {e}")
                sync_stats = None
        
        # Fallback to stubs if API failed or stubs preferred
        if sync_stats is None:
            logger.info(f"Using stub data for {sport_key}...")
            sync_stats = await sync_games_and_lines(
                db, sport_key, include_props=True, use_stubs=True
            )
            used_stubs = True
            logger.info(f"Stub sync: {sync_stats}")
        
        # =================================================================
        # Step 2: Clear old data ONLY if we got new data
        # =================================================================
        new_games = sync_stats.get("games_created", 0) + sync_stats.get("games_updated", 0)
        new_props = sync_stats.get("props_added", 0)
        
        if new_games > 0 or new_props > 0:
            logger.info(f"New data confirmed ({new_games} games, {new_props} props), clearing stale data...")
            clear_stats = await clear_stale_games(db, sport_key)
            logger.info(f"Cleared: {clear_stats}")
        else:
            logger.warning("No new data fetched, keeping existing data")
        
        # =================================================================
        # Step 3: Generate picks
        # =================================================================
        logger.info(f"Generating picks for {sport_key} (used_stubs={used_stubs})...")
        picks_result = await generate_picks(
            db,
            sport_key,
            min_ev=0.0,
            min_confidence=0.5,
            use_stubs=used_stubs,
        )
        logger.info(f"Generated: {picks_result}")
        
        return {
            "status": "success",
            "sport": sport,
            "used_stubs": used_stubs,
            "clear_stats": clear_stats,
            "sync_stats": sync_stats,
            "picks_result": picks_result,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error refreshing picks: {e}")
        raise HTTPException(status_code=500, detail=str(e)[:200])
