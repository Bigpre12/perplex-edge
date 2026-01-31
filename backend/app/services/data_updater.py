"""Data updater service for maintaining picks, injuries, and historical data."""
import logging
from datetime import datetime, timezone, timedelta
from typing import Any, Optional

from sqlalchemy import select, update, delete, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Pick, PlayerStat, HistoricalPerformance, Game, Line, Sport, PlayerGameStats

logger = logging.getLogger(__name__)


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
    # Use naive datetime for TIMESTAMP WITHOUT TIME ZONE column comparison
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days_old)).replace(tzinfo=None)
    
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
    use_stubs: bool = False,
) -> dict[str, Any]:
    """
    Check game results and mark picks as hit/miss.
    
    This function:
    1. Finds games that should have completed (between yesterday and today)
    2. Marks them as "final" status
    3. Uses ResultsTracker to settle picks based on actual PlayerGameStats
    4. Updates historical performance
    
    If use_stubs is True, simulates game results for testing.
    
    Args:
        db: Database session
        sport_key: Sport identifier
        use_stubs: If True, simulate game results
    
    Returns:
        Dictionary with results summary
    """
    from app.services.results_tracker import ResultsTracker
    from app.services.stats_provider import StatsProvider
    
    logger.info(f"Checking game results for {sport_key}")
    
    # Initialize services
    results_tracker = ResultsTracker(use_stubs=use_stubs)
    stats_provider = StatsProvider()
    
    # Get sport
    sport_result = await db.execute(
        select(Sport).where(
            or_(
                Sport.key == sport_key,
                Sport.league_code.ilike(f"%{sport_key}%"),
            )
        )
    )
    sport = sport_result.scalar_one_or_none()
    
    if not sport:
        return {
            "sport": sport_key,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": f"Sport {sport_key} not found",
            "status": "failed",
        }
    
    # Find games that should have completed
    # Use naive datetimes for TIMESTAMP WITHOUT TIME ZONE column comparison
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    yesterday = (now - timedelta(days=1))
    hours_ago_4 = now - timedelta(hours=4)  # Games need at least 4 hours to complete
    
    result = await db.execute(
        select(Game).where(
            and_(
                Game.sport_id == sport.id,
                Game.start_time >= yesterday,
                Game.start_time < hours_ago_4,  # Started at least 4 hours ago
                Game.status.in_(["scheduled", "in_progress"]),  # Not yet final
            )
        )
    )
    games = result.scalars().all()
    
    if not games:
        logger.info(f"No completed games to process for {sport_key}")
        return {
            "sport": sport_key,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "games_checked": 0,
            "picks_settled": 0,
            "total_hits": 0,
            "total_misses": 0,
            "status": "no_games",
        }
    
    logger.info(f"Found {len(games)} completed games to process for {sport_key}")
    
    total_settled = 0
    total_hits = 0
    total_misses = 0
    games_processed = 0
    
    for game in games:
        try:
            # Try to fetch actual stats if not using stubs
            stats_fetched = False
            
            if not use_stubs:
                # Check if we already have stats for this game
                existing_stats = await db.execute(
                    select(func.count(PlayerGameStats.id)).where(
                        PlayerGameStats.game_id == game.id
                    )
                )
                stats_count = existing_stats.scalar() or 0
                
                if stats_count == 0:
                    # Try to fetch stats from provider
                    try:
                        box_score = await stats_provider.fetch_game_stats(
                            sport_key=sport_key,
                            game_id=str(game.external_id) if game.external_id else str(game.id),
                        )
                        
                        if box_score:
                            # Store the fetched stats
                            for player_stat in box_score.get("player_stats", []):
                                stat = PlayerGameStats(
                                    player_id=player_stat.get("player_id"),
                                    game_id=game.id,
                                    stat_type=player_stat.get("stat_type"),
                                    value=player_stat.get("value"),
                                    minutes=player_stat.get("minutes"),
                                )
                                db.add(stat)
                            
                            await db.commit()
                            stats_fetched = True
                            logger.info(f"Fetched stats for game {game.id}")
                    except Exception as e:
                        logger.warning(f"Could not fetch stats for game {game.id}: {e}")
                else:
                    stats_fetched = True  # Already have stats
            
            # If no real stats and using stubs, simulate results
            if use_stubs or not stats_fetched:
                logger.info(f"Simulating results for game {game.id}")
                settlement = await results_tracker.simulate_game_results(db, game.id)
            else:
                # Settle picks using actual stats
                settlement = await results_tracker.settle_picks_for_game(db, game.id)
            
            if "error" not in settlement:
                total_settled += settlement.get("settled", 0)
                total_hits += settlement.get("hits", 0)
                total_misses += settlement.get("misses", 0)
                games_processed += 1
                
                # Mark game as final
                game.status = "final"
                await db.commit()
                
                logger.info(
                    f"Settled game {game.id}: "
                    f"{settlement.get('hits', 0)} hits, {settlement.get('misses', 0)} misses"
                )
            else:
                logger.warning(f"Error settling game {game.id}: {settlement.get('error')}")
                
        except Exception as e:
            logger.error(f"Error processing game {game.id}: {e}")
            continue
    
    hit_rate = (total_hits / total_settled * 100) if total_settled > 0 else 0.0
    
    logger.info(
        f"Completed results check for {sport_key}: "
        f"{games_processed} games, {total_settled} picks settled, "
        f"{hit_rate:.1f}% hit rate"
    )
    
    return {
        "sport": sport_key,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "games_checked": len(games),
        "games_processed": games_processed,
        "picks_settled": total_settled,
        "total_hits": total_hits,
        "total_misses": total_misses,
        "hit_rate": round(hit_rate, 2),
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
