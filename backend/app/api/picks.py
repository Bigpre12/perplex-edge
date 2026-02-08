"""Model Picks API endpoints."""

import logging
from typing import Optional
from datetime import datetime, timedelta, timezone

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
    # Basketball
    "nba": "basketball_nba",
    "ncaab": "basketball_ncaab",
    "wnba": "basketball_wnba",
    # Football
    "nfl": "americanfootball_nfl",
    "ncaaf": "americanfootball_ncaaf",
    # Baseball
    "mlb": "baseball_mlb",
    # Hockey
    "nhl": "icehockey_nhl",
    # Tennis
    "atp": "tennis_atp",
    "wta": "tennis_wta",
    # Golf
    "pga": "golf_pga_tour",
    # Soccer
    "epl": "soccer_epl",
    "ucl": "soccer_uefa_champs_league",
    "mls": "soccer_usa_mls",
    # MMA/UFC
    "ufc": "mma_mixed_martial_arts",
    "mma": "mma_mixed_martial_arts",
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
            game_time=game.start_time if game else datetime.now(timezone.utc),
        ))

    return ModelPickList(items=items, total=total or 0)

@router.get("/top", response_model=ModelPickList)
async def get_top_picks(
    sport: Optional[str] = Query(None, description="Filter by sport"),
    limit: int = Query(10, le=50),
    db: AsyncSession = Depends(get_db),
):
    """Get top picks by expected value for today's games."""
    from zoneinfo import ZoneInfo
    EASTERN_TZ = ZoneInfo("America/New_York")
    
    # Use Eastern time for "today" (consistent with other endpoints)
    now_et = datetime.now(EASTERN_TZ)
    today_start_et = now_et.replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow_start_et = today_start_et + timedelta(days=1)
    
    # Convert to UTC naive for PostgreSQL
    today = today_start_et.astimezone(timezone.utc).replace(tzinfo=None)
    tomorrow = tomorrow_start_et.astimezone(timezone.utc).replace(tzinfo=None)

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
            game_time=game.start_time if game else datetime.now(timezone.utc),
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
    Full refresh with multi-provider cascade.
    
    Cascade order:
    1. The Odds API (primary)
    2. BetStack API (secondary)  
    3. Cached data (tertiary)
    4. Stub data (last resort)
    
    This ensures data availability even when multiple APIs fail.
    """
    from app.services.etl_games_and_lines import clear_stale_games, sync_games_and_lines
    from app.services.odds_cache import save_to_cache, load_from_cache
    from app.core.config import get_settings
    
    settings = get_settings()
    prefer_stubs = settings.scheduler_use_stubs
    
    try:
        sport_key = SPORT_KEY_MAP.get(sport.lower())
        if not sport_key:
            raise HTTPException(status_code=400, detail=f"Unknown sport: {sport}")
        
        sync_stats = None
        data_source = "none"
        clear_stats = {"skipped": True, "reason": "no_new_data"}
        
        # =================================================================
        # Multi-Provider Cascade
        # =================================================================
        
        if not prefer_stubs:
            # ----- Step 1: Try The Odds API (Primary) -----
            logger.info(f"[1/4] Trying The Odds API for {sport_key}...")
            try:
                sync_stats = await sync_games_and_lines(
                    db, sport_key, include_props=True, use_stubs=False,
                    provider="odds_api"  # Primary provider
                )
                
                if _is_sync_successful(sync_stats):
                    logger.info(f"The Odds API success: {sync_stats}")
                    data_source = "odds_api"
                    # Cache successful data
                    save_to_cache(sport_key, sync_stats)
                else:
                    logger.warning(f"The Odds API returned incomplete data")
                    sync_stats = None
            except Exception as e:
                logger.warning(f"The Odds API failed: {e}")
                sync_stats = None
            
            # ----- Step 2: Try BetStack API (Secondary) -----
            if sync_stats is None and settings.betstack_api_key:
                logger.info(f"[2/4] Trying BetStack API for {sport_key}...")
                try:
                    sync_stats = await sync_games_and_lines(
                        db, sport_key, include_props=True, use_stubs=False,
                        provider="betstack"  # Secondary provider
                    )
                    
                    if _is_sync_successful(sync_stats):
                        logger.info(f"BetStack API success: {sync_stats}")
                        data_source = "betstack"
                        save_to_cache(sport_key, sync_stats)
                    else:
                        logger.warning(f"BetStack API returned incomplete data")
                        sync_stats = None
                except Exception as e:
                    logger.warning(f"BetStack API failed: {e}")
                    sync_stats = None
            
            # ----- Step 3: Try Cached Data (Tertiary) -----
            if sync_stats is None:
                logger.info(f"[3/4] Trying cached data for {sport_key}...")
                cached = load_from_cache(sport_key)
                if cached:
                    logger.info(f"Using cached data for {sport_key}")
                    data_source = "cache"
                    sync_stats = cached
                else:
                    logger.warning("No valid cache available")
        
        # ----- Step 4: Fallback to Stubs (Last Resort) -----
        if sync_stats is None:
            logger.info(f"[4/4] Using stub data for {sport_key}...")
            sync_stats = await sync_games_and_lines(
                db, sport_key, include_props=True, use_stubs=True
            )
            data_source = "stubs"
            logger.info(f"Stub sync: {sync_stats}")
        
        # =================================================================
        # Clear old data ONLY if we got new data
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
        # Generate picks
        # =================================================================
        use_stubs_for_picks = data_source == "stubs"
        logger.info(f"Generating picks for {sport_key} (source={data_source})...")
        picks_result = await generate_picks(
            db,
            sport_key,
            min_ev=0.0,
            min_confidence=0.5,
            use_stubs=use_stubs_for_picks,
        )
        logger.info(f"Generated: {picks_result}")
        
        return {
            "status": "success",
            "sport": sport,
            "data_source": data_source,
            "clear_stats": clear_stats,
            "sync_stats": sync_stats,
            "picks_result": picks_result,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error refreshing picks: {e}")
        raise HTTPException(status_code=500, detail=str(e)[:200])

def _is_sync_successful(sync_stats: dict) -> bool:
    """Check if a sync operation returned useful data."""
    if not sync_stats:
        return False
    
    has_errors = len(sync_stats.get("errors", [])) > 0
    has_games = sync_stats.get("games_created", 0) > 0 or sync_stats.get("games_updated", 0) > 0
    has_props = sync_stats.get("props_added", 0) > 0
    
    # Success if we have games/props and either no errors or errors but still got props
    if has_games or has_props:
        if has_errors and not has_props:
            return False  # Errors with no props = failure
        return True
    
    return False
