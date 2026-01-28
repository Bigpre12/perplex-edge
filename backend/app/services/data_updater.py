"""Data updater service for maintaining picks, injuries, and historical data."""
import logging
from datetime import datetime, timezone, timedelta
from typing import Any, Optional

from sqlalchemy import select, update, delete, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Pick, PlayerStat, HistoricalPerformance, Game, Line

logger = logging.getLogger(__name__)


# =============================================================================
# Injury Reports
# =============================================================================

async def fetch_injury_reports(
    db: AsyncSession,
    sport_key: str,
) -> dict[str, Any]:
    """
    Fetch and process injury reports for a sport.
    
    In production, this would call an external injury API.
    For now, returns stub data structure.
    
    Args:
        db: Database session
        sport_key: Sport identifier (e.g., 'basketball_nba')
    
    Returns:
        Dictionary with injury report summary
    """
    logger.info(f"Fetching injury reports for {sport_key}")
    
    # TODO: Integrate with real injury API
    # For now, return structure for future implementation
    return {
        "sport": sport_key,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "injuries": [],
        "updates_applied": 0,
        "status": "stub_data",
    }


# =============================================================================
# Line Movement Detection
# =============================================================================

def detect_line_movement(
    current_odds: float,
    historical_odds: float,
    threshold: float = 10.0,
) -> dict[str, Any]:
    """
    Detect significant line movement between current and historical odds.
    
    Args:
        current_odds: Current American odds
        historical_odds: Previous American odds
        threshold: Minimum movement to flag (in odds points)
    
    Returns:
        Dictionary with movement analysis
    """
    movement = current_odds - historical_odds
    abs_movement = abs(movement)
    
    # Determine direction
    if movement > 0:
        direction = "up" if current_odds > 0 else "less_favorite"
    elif movement < 0:
        direction = "down" if current_odds > 0 else "more_favorite"
    else:
        direction = "none"
    
    # Flag significant movements
    is_significant = abs_movement >= threshold
    
    return {
        "current_odds": current_odds,
        "historical_odds": historical_odds,
        "movement": movement,
        "abs_movement": abs_movement,
        "direction": direction,
        "is_significant": is_significant,
        "threshold": threshold,
    }


async def check_line_movements(
    db: AsyncSession,
    hours_back: int = 1,
    threshold: float = 10.0,
) -> dict[str, Any]:
    """
    Check for significant line movements across all current picks.
    
    Args:
        db: Database session
        hours_back: Hours to look back for historical comparison
        threshold: Minimum movement to flag
    
    Returns:
        Dictionary with movement summary
    """
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours_back)
    movements = []
    
    # Get current picks
    result = await db.execute(select(Pick))
    picks = result.scalars().all()
    
    for pick in picks:
        # In production, compare with historical Line records
        # For now, just log that we're checking
        movements.append({
            "pick_id": pick.id,
            "player_name": pick.player_name,
            "current_odds": pick.odds,
            "checked": True,
        })
    
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "picks_checked": len(picks),
        "significant_movements": 0,
        "movements": movements[:10],  # Limit output
    }


# =============================================================================
# Confidence Updates
# =============================================================================

async def update_pick_confidence(
    db: AsyncSession,
    pick_id: int,
    new_confidence: Optional[float] = None,
    new_ev: Optional[float] = None,
    new_odds: Optional[int] = None,
) -> bool:
    """
    Update a pick's confidence and related metrics based on new data.
    
    Args:
        db: Database session
        pick_id: Pick ID to update
        new_confidence: New confidence score (0-1)
        new_ev: New EV percentage
        new_odds: New odds value
    
    Returns:
        True if updated successfully
    """
    try:
        updates = {}
        
        if new_confidence is not None:
            updates["confidence"] = new_confidence
        if new_ev is not None:
            updates["ev_percentage"] = new_ev
        if new_odds is not None:
            updates["odds"] = new_odds
        
        if not updates:
            return False
        
        await db.execute(
            update(Pick)
            .where(Pick.id == pick_id)
            .values(**updates)
        )
        await db.commit()
        
        logger.info(f"Updated pick {pick_id} with: {updates}")
        return True
    
    except Exception as e:
        logger.error(f"Error updating pick {pick_id}: {e}")
        await db.rollback()
        return False


# =============================================================================
# Archive Old Picks
# =============================================================================

async def archive_old_picks(
    db: AsyncSession,
    days_old: int = 7,
) -> int:
    """
    Archive picks older than specified days.
    
    Moves completed game picks to historical tracking.
    
    Args:
        db: Database session
        days_old: Days threshold for archiving
    
    Returns:
        Number of picks archived
    """
    cutoff = datetime.now(timezone.utc) - timedelta(days=days_old)
    
    try:
        # Find old picks
        result = await db.execute(
            select(Pick).where(Pick.created_at < cutoff)
        )
        old_picks = result.scalars().all()
        
        archived_count = 0
        
        for pick in old_picks:
            # Update historical performance if we have result data
            if pick.hit_rate is not None:
                await _update_historical_for_pick(db, pick)
                archived_count += 1
        
        # Delete archived picks
        if archived_count > 0:
            await db.execute(
                delete(Pick).where(Pick.created_at < cutoff)
            )
            await db.commit()
        
        logger.info(f"Archived {archived_count} old picks")
        return archived_count
    
    except Exception as e:
        logger.error(f"Error archiving picks: {e}")
        await db.rollback()
        return 0


async def _update_historical_for_pick(
    db: AsyncSession,
    pick: Pick,
) -> None:
    """Update historical performance record for a pick."""
    if not pick.player_name or not pick.stat_type:
        return
    
    # Find or create historical record
    result = await db.execute(
        select(HistoricalPerformance).where(
            and_(
                HistoricalPerformance.player_name == pick.player_name,
                HistoricalPerformance.stat_type == pick.stat_type,
            )
        )
    )
    record = result.scalar_one_or_none()
    
    if record:
        # Update existing
        record.total_picks += 1
        if pick.hit_rate and pick.hit_rate > 0.5:
            record.hits += 1
        else:
            record.misses += 1
        record.hit_rate_percentage = round(
            record.hits / record.total_picks * 100, 2
        )
        record.avg_ev = round(
            (record.avg_ev * (record.total_picks - 1) + pick.ev_percentage) / record.total_picks,
            2
        )
    else:
        # Create new
        is_hit = pick.hit_rate and pick.hit_rate > 0.5
        new_record = HistoricalPerformance(
            player_name=pick.player_name,
            stat_type=pick.stat_type,
            total_picks=1,
            hits=1 if is_hit else 0,
            misses=0 if is_hit else 1,
            hit_rate_percentage=100.0 if is_hit else 0.0,
            avg_ev=pick.ev_percentage,
        )
        db.add(new_record)


# =============================================================================
# Game Results Checking
# =============================================================================

async def check_game_results(
    db: AsyncSession,
    sport_key: str,
) -> dict[str, Any]:
    """
    Check game results and mark picks as hit/miss.
    
    In production, this would:
    1. Fetch completed game results from API
    2. Compare actual stats to pick lines
    3. Update picks with hit/miss status
    4. Update historical performance
    
    Args:
        db: Database session
        sport_key: Sport identifier
    
    Returns:
        Dictionary with results summary
    """
    logger.info(f"Checking game results for {sport_key}")
    
    # Find games that should have completed
    yesterday = datetime.now(timezone.utc) - timedelta(days=1)
    today = datetime.now(timezone.utc)
    
    result = await db.execute(
        select(Game).where(
            and_(
                Game.start_time >= yesterday,
                Game.start_time < today,
                Game.status == "scheduled",
            )
        )
    )
    games = result.scalars().all()
    
    results_checked = 0
    picks_updated = 0
    
    for game in games:
        # TODO: Fetch actual game results from API
        # For now, mark game as needing result check
        
        # Get picks for this game
        picks_result = await db.execute(
            select(Pick).where(Pick.game_id == game.id)
        )
        game_picks = picks_result.scalars().all()
        
        for pick in game_picks:
            # TODO: Compare actual stats to line and determine hit/miss
            # This requires fetching actual player stats from completed game
            results_checked += 1
    
    logger.info(f"Checked {results_checked} picks for {sport_key}")
    
    return {
        "sport": sport_key,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "games_checked": len(games),
        "picks_checked": results_checked,
        "picks_updated": picks_updated,
        "status": "completed",
    }


# =============================================================================
# Update Historical Stats
# =============================================================================

async def update_historical_stats(db: AsyncSession) -> dict[str, Any]:
    """
    Recalculate historical performance stats for all players.
    
    Returns:
        Dictionary with update summary
    """
    logger.info("Updating historical stats...")
    
    # Get all player stats grouped by player and stat type
    result = await db.execute(
        select(
            PlayerStat.player_name,
            PlayerStat.stat_type,
            func.count(PlayerStat.id).label("total"),
            func.sum(
                func.case((PlayerStat.result == "hit", 1), else_=0)
            ).label("hits"),
        )
        .group_by(PlayerStat.player_name, PlayerStat.stat_type)
    )
    stats = result.all()
    
    updated = 0
    
    for stat in stats:
        player_name, stat_type, total, hits = stat
        misses = total - hits
        hit_rate = round(hits / total * 100, 2) if total > 0 else 0.0
        
        # Update or create historical record
        existing = await db.execute(
            select(HistoricalPerformance).where(
                and_(
                    HistoricalPerformance.player_name == player_name,
                    HistoricalPerformance.stat_type == stat_type,
                )
            )
        )
        record = existing.scalar_one_or_none()
        
        if record:
            record.total_picks = total
            record.hits = hits
            record.misses = misses
            record.hit_rate_percentage = hit_rate
        else:
            new_record = HistoricalPerformance(
                player_name=player_name,
                stat_type=stat_type,
                total_picks=total,
                hits=hits,
                misses=misses,
                hit_rate_percentage=hit_rate,
                avg_ev=0.0,
            )
            db.add(new_record)
        
        updated += 1
    
    await db.commit()
    logger.info(f"Updated {updated} historical records")
    
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "records_updated": updated,
        "status": "completed",
    }
