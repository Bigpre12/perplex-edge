"""
NCAAB Odds Service for fetching, storing, and analyzing college basketball betting odds.

Implements cascade fetch: OddsAPI -> BetStack -> JSON Backup
"""

import logging
from datetime import date, datetime
from typing import Any, Optional

from sqlalchemy import select, delete, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.ncaab_odds import LiveOddsNCAAB, HistoricalOddsNCAAB
from app.models import Sport
from app.services.ncaab_backup import (
    save_backup,
    load_backup,
    get_latest_backup,
    backup_exists,
)
from app.services.odds_provider import XYZOddsProvider, BetStackProvider

logger = logging.getLogger(__name__)

# NCAAB sport key for OddsAPI
NCAAB_SPORT_KEY = "basketball_ncaab"

# Default bookmakers to track
DEFAULT_BOOKMAKERS = ["draftkings", "fanduel", "betmgm", "caesars", "pointsbet"]


async def ensure_ncaab_sport_exists(db: AsyncSession) -> Sport:
    """
    Ensure the NCAAB sport exists in the database.
    Creates it if it doesn't exist.
    
    Returns:
        The NCAAB Sport record
    """
    result = await db.execute(
        select(Sport).where(Sport.league_code == "NCAAB")
    )
    sport = result.scalar_one_or_none()
    
    if not sport:
        sport = Sport(name="NCAA Basketball", league_code="NCAAB")
        db.add(sport)
        await db.commit()
        logger.info("Created NCAAB sport in database")
    
    return sport


def _get_current_ncaab_season() -> str:
    """
    Get current NCAAB season string.
    
    NCAAB season typically runs November to March/April.
    Season format: "2025-2026"
    
    Returns:
        Season string like "2025-2026"
    """
    now = datetime.utcnow()
    year = now.year
    month = now.month
    
    # Season starts in November
    if month >= 11:  # November onwards = new season
        return f"{year}-{year + 1}"
    else:  # Before November = previous season
        return f"{year - 1}-{year}"


async def fetch_ncaab_odds_cascade(
    bookmakers: Optional[list[str]] = None,
) -> tuple[list[dict[str, Any]], str]:
    """
    Fetch NCAAB odds using cascade: OddsAPI -> BetStack -> JSON backup.
    
    Args:
        bookmakers: Optional list of bookmakers to fetch
    
    Returns:
        Tuple of (odds_data, source) where source is 'oddsapi', 'betstack', or 'backup'
    """
    settings = get_settings()
    bookmakers = bookmakers or DEFAULT_BOOKMAKERS
    
    # Step 1: Try OddsAPI (primary)
    if settings.odds_api_key:
        logger.info("Trying OddsAPI for NCAAB odds...")
        try:
            async with XYZOddsProvider(use_stubs=False) as provider:
                games = await provider.fetch_games(NCAAB_SPORT_KEY)
                
                if games:
                    odds_data = _transform_odds_response(games, "oddsapi")
                    logger.info(f"OddsAPI returned {len(odds_data)} NCAAB odds records")
                    return odds_data, "oddsapi"
                else:
                    logger.warning("OddsAPI returned no NCAAB data")
        except Exception as e:
            logger.warning(f"OddsAPI failed: {e}")
    
    # Step 2: Try BetStack (secondary)
    if settings.betstack_api_key:
        logger.info("Trying BetStack API for NCAAB odds...")
        try:
            async with BetStackProvider(use_stubs=False) as provider:
                games = await provider.fetch_games(NCAAB_SPORT_KEY)
                
                if games:
                    odds_data = _transform_odds_response(games, "betstack")
                    logger.info(f"BetStack returned {len(odds_data)} NCAAB odds records")
                    return odds_data, "betstack"
                else:
                    logger.warning("BetStack returned no NCAAB data")
        except Exception as e:
            logger.warning(f"BetStack failed: {e}")
    
    # Step 3: Load from JSON backup (fallback)
    logger.info("Trying JSON backup for NCAAB odds...")
    try:
        backup_data, backup_date = get_latest_backup()
        if backup_data:
            logger.info(f"Loaded {len(backup_data)} records from backup ({backup_date})")
            return backup_data, "backup"
    except Exception as e:
        logger.warning(f"Backup load failed: {e}")
    
    # All sources failed
    logger.error("All data sources failed for NCAAB odds")
    return [], "none"


def _transform_odds_response(
    games: list[Any],
    source: str,
) -> list[dict[str, Any]]:
    """
    Transform API response to standardized odds format.
    
    Args:
        games: Raw games data from API
        source: Data source identifier
    
    Returns:
        List of standardized odds dictionaries
    """
    season = _get_current_ncaab_season()
    odds_list = []
    
    for game in games:
        game_id = game.external_game_id if hasattr(game, 'external_game_id') else game.get('id', '')
        home_team = game.home_team if hasattr(game, 'home_team') else game.get('home_team', '')
        away_team = game.away_team if hasattr(game, 'away_team') else game.get('away_team', '')
        
        # Extract bookmaker odds
        bookmakers_data = game.bookmakers if hasattr(game, 'bookmakers') else game.get('bookmakers', [])
        
        for bookmaker in bookmakers_data:
            bm_key = bookmaker.get('key', 'unknown') if isinstance(bookmaker, dict) else getattr(bookmaker, 'key', 'unknown')
            
            # Extract h2h (moneyline) odds
            markets = bookmaker.get('markets', []) if isinstance(bookmaker, dict) else getattr(bookmaker, 'markets', [])
            
            for market in markets:
                market_key = market.get('key', '') if isinstance(market, dict) else getattr(market, 'key', '')
                
                if market_key == 'h2h':  # Head to head / moneyline
                    outcomes = market.get('outcomes', []) if isinstance(market, dict) else getattr(market, 'outcomes', [])
                    
                    home_odds = None
                    away_odds = None
                    draw_odds = None
                    
                    for outcome in outcomes:
                        name = outcome.get('name', '') if isinstance(outcome, dict) else getattr(outcome, 'name', '')
                        price = outcome.get('price', 0) if isinstance(outcome, dict) else getattr(outcome, 'price', 0)
                        
                        if name == home_team:
                            home_odds = price
                        elif name == away_team:
                            away_odds = price
                        elif name.lower() == 'draw':
                            draw_odds = price
                    
                    if home_odds and away_odds:
                        odds_list.append({
                            "game_id": game_id,
                            "home_team": home_team,
                            "away_team": away_team,
                            "home_odds": home_odds,
                            "away_odds": away_odds,
                            "draw_odds": draw_odds,
                            "bookmaker": bm_key,
                            "season": season,
                            "source": source,
                        })
    
    return odds_list


async def save_live_odds(
    db: AsyncSession,
    odds_data: list[dict[str, Any]],
    clear_existing: bool = True,
) -> dict[str, Any]:
    """
    Save live NCAAB odds to database.
    
    Args:
        db: Database session
        odds_data: List of odds dictionaries
        clear_existing: Whether to clear existing live odds first
    
    Returns:
        Statistics about the save operation
    """
    stats = {
        "cleared": 0,
        "inserted": 0,
        "errors": [],
    }
    
    try:
        # Clear existing live odds if requested
        if clear_existing:
            result = await db.execute(delete(LiveOddsNCAAB))
            stats["cleared"] = result.rowcount
            logger.info(f"Cleared {stats['cleared']} existing live NCAAB odds")
        
        # Insert new odds
        for odds in odds_data:
            try:
                live_odds = LiveOddsNCAAB(
                    game_id=odds["game_id"],
                    home_team=odds["home_team"],
                    away_team=odds["away_team"],
                    home_odds=odds["home_odds"],
                    away_odds=odds["away_odds"],
                    draw_odds=odds.get("draw_odds"),
                    bookmaker=odds["bookmaker"],
                    season=odds["season"],
                    timestamp=datetime.utcnow(),
                )
                db.add(live_odds)
                stats["inserted"] += 1
            except Exception as e:
                stats["errors"].append(str(e)[:100])
        
        await db.commit()
        logger.info(f"Saved {stats['inserted']} live NCAAB odds records")
        
    except Exception as e:
        stats["errors"].append(str(e)[:200])
        logger.error(f"Error saving live odds: {e}")
        await db.rollback()
    
    return stats


async def create_daily_snapshot(
    db: AsyncSession,
    snapshot_date: Optional[date] = None,
) -> dict[str, Any]:
    """
    Create daily snapshot of live odds in historical table.
    
    Args:
        db: Database session
        snapshot_date: Date for snapshot (defaults to today)
    
    Returns:
        Statistics about the snapshot operation
    """
    snapshot_date = snapshot_date or date.today()
    stats = {
        "snapshot_date": snapshot_date.isoformat(),
        "records_copied": 0,
        "already_exists": False,
        "errors": [],
    }
    
    try:
        # Check if snapshot already exists for this date
        existing = await db.execute(
            select(func.count(HistoricalOddsNCAAB.id)).where(
                HistoricalOddsNCAAB.snapshot_date == snapshot_date
            )
        )
        existing_count = existing.scalar()
        
        if existing_count > 0:
            logger.info(f"Snapshot already exists for {snapshot_date} ({existing_count} records)")
            stats["already_exists"] = True
            stats["records_copied"] = existing_count
            return stats
        
        # Get all live odds
        live_result = await db.execute(select(LiveOddsNCAAB))
        live_odds = live_result.scalars().all()
        
        if not live_odds:
            logger.warning("No live odds to snapshot")
            return stats
        
        # Copy to historical
        for live in live_odds:
            historical = HistoricalOddsNCAAB(
                game_id=live.game_id,
                home_team=live.home_team,
                away_team=live.away_team,
                home_odds=live.home_odds,
                away_odds=live.away_odds,
                draw_odds=live.draw_odds,
                bookmaker=live.bookmaker,
                snapshot_date=snapshot_date,
                season=live.season,
                result=None,  # Will be updated after game completes
            )
            db.add(historical)
            stats["records_copied"] += 1
        
        await db.commit()
        logger.info(f"Created snapshot for {snapshot_date}: {stats['records_copied']} records")
        
    except Exception as e:
        stats["errors"].append(str(e)[:200])
        logger.error(f"Error creating snapshot: {e}")
        await db.rollback()
    
    return stats


async def update_game_results(
    db: AsyncSession,
    game_id: str,
    result: str,
) -> dict[str, Any]:
    """
    Update result for a completed game in historical records.
    
    Args:
        db: Database session
        game_id: Game identifier
        result: Game result ('home', 'away')
    
    Returns:
        Update statistics
    """
    stats = {
        "game_id": game_id,
        "result": result,
        "records_updated": 0,
    }
    
    if result not in ('home', 'away'):
        raise ValueError(f"Invalid result: {result}. Must be 'home' or 'away'")
    
    try:
        # Update all historical records for this game
        from sqlalchemy import update
        stmt = (
            update(HistoricalOddsNCAAB)
            .where(HistoricalOddsNCAAB.game_id == game_id)
            .values(result=result)
        )
        result_obj = await db.execute(stmt)
        stats["records_updated"] = result_obj.rowcount
        
        await db.commit()
        logger.info(f"Updated result for game {game_id}: {result} ({stats['records_updated']} records)")
        
    except Exception as e:
        logger.error(f"Error updating game result: {e}")
        await db.rollback()
        raise
    
    return stats


async def get_live_odds(
    db: AsyncSession,
    season: Optional[str] = None,
    bookmaker: Optional[str] = None,
) -> list[dict[str, Any]]:
    """
    Get live NCAAB odds from database.
    
    Args:
        db: Database session
        season: Optional season filter
        bookmaker: Optional bookmaker filter
    
    Returns:
        List of live odds as dictionaries
    """
    query = select(LiveOddsNCAAB)
    
    if season:
        query = query.where(LiveOddsNCAAB.season == season)
    if bookmaker:
        query = query.where(LiveOddsNCAAB.bookmaker == bookmaker)
    
    query = query.order_by(LiveOddsNCAAB.timestamp.desc())
    
    result = await db.execute(query)
    odds = result.scalars().all()
    
    return [o.to_dict() for o in odds]


async def get_historical_odds(
    db: AsyncSession,
    season: Optional[str] = None,
    bookmaker: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> list[dict[str, Any]]:
    """
    Get historical NCAAB odds from database.
    
    Args:
        db: Database session
        season: Optional season filter
        bookmaker: Optional bookmaker filter
        start_date: Optional start date filter
        end_date: Optional end date filter
    
    Returns:
        List of historical odds as dictionaries
    """
    query = select(HistoricalOddsNCAAB)
    
    filters = []
    if season:
        filters.append(HistoricalOddsNCAAB.season == season)
    if bookmaker:
        filters.append(HistoricalOddsNCAAB.bookmaker == bookmaker)
    if start_date:
        filters.append(HistoricalOddsNCAAB.snapshot_date >= start_date)
    if end_date:
        filters.append(HistoricalOddsNCAAB.snapshot_date <= end_date)
    
    if filters:
        query = query.where(and_(*filters))
    
    query = query.order_by(HistoricalOddsNCAAB.snapshot_date.desc())
    
    result = await db.execute(query)
    odds = result.scalars().all()
    
    return [o.to_dict() for o in odds]


async def calculate_hit_rates(
    db: AsyncSession,
    season: Optional[str] = None,
    bookmaker: Optional[str] = None,
) -> dict[str, Any]:
    """
    Calculate hit rates from historical odds data.
    
    Analyzes how often favorites won based on odds.
    
    Args:
        db: Database session
        season: Optional season filter
        bookmaker: Optional bookmaker filter
    
    Returns:
        Hit rate statistics
    """
    query = select(HistoricalOddsNCAAB).where(
        HistoricalOddsNCAAB.result.isnot(None)
    )
    
    if season:
        query = query.where(HistoricalOddsNCAAB.season == season)
    if bookmaker:
        query = query.where(HistoricalOddsNCAAB.bookmaker == bookmaker)
    
    result = await db.execute(query)
    historical = result.scalars().all()
    
    if not historical:
        return {
            "total_games": 0,
            "message": "No settled games found",
        }
    
    # Calculate statistics
    total = len(historical)
    favorites_won = sum(1 for h in historical if h.favorite_won)
    underdogs_won = sum(1 for h in historical if h.favorite_won is False)
    
    # Group by bookmaker
    by_bookmaker = {}
    for h in historical:
        bm = h.bookmaker
        if bm not in by_bookmaker:
            by_bookmaker[bm] = {"total": 0, "favorites_won": 0}
        by_bookmaker[bm]["total"] += 1
        if h.favorite_won:
            by_bookmaker[bm]["favorites_won"] += 1
    
    # Calculate hit rates per bookmaker
    bookmaker_stats = {}
    for bm, data in by_bookmaker.items():
        hit_rate = (data["favorites_won"] / data["total"] * 100) if data["total"] > 0 else 0
        bookmaker_stats[bm] = {
            "total_games": data["total"],
            "favorites_won": data["favorites_won"],
            "hit_rate": round(hit_rate, 2),
        }
    
    return {
        "total_games": total,
        "favorites_won": favorites_won,
        "underdogs_won": underdogs_won,
        "overall_favorite_hit_rate": round(favorites_won / total * 100, 2) if total > 0 else 0,
        "by_bookmaker": bookmaker_stats,
    }


async def sync_ncaab_odds(db: AsyncSession) -> dict[str, Any]:
    """
    Full NCAAB odds sync: fetch -> save -> backup.
    
    Args:
        db: Database session
    
    Returns:
        Sync statistics
    """
    stats = {
        "fetch_source": "none",
        "records_fetched": 0,
        "save_stats": {},
        "backup_saved": False,
    }
    
    # Fetch odds using cascade
    odds_data, source = await fetch_ncaab_odds_cascade()
    stats["fetch_source"] = source
    stats["records_fetched"] = len(odds_data)
    
    if not odds_data:
        logger.warning("No NCAAB odds data to sync")
        return stats
    
    # Save to database
    stats["save_stats"] = await save_live_odds(db, odds_data)
    
    # Save JSON backup
    try:
        save_backup([o for o in odds_data])
        stats["backup_saved"] = True
    except Exception as e:
        logger.error(f"Failed to save backup: {e}")
    
    return stats
