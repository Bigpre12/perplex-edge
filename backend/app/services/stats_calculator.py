"""Stats calculator service for historical performance analysis."""
import logging
from datetime import datetime, timezone, timedelta
from typing import Any, Optional

from sqlalchemy import select, func, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    PlayerStat,
    HistoricalPerformance,
    Pick,
    PickResult,
    ModelPick,
    Player,
    Market,
    OddsSnapshot,
    Game,
)

logger = logging.getLogger(__name__)


async def calculate_historical_hit_rate(
    db: AsyncSession,
    player_name: str,
    stat_type: str,
) -> dict[str, Any]:
    """
    Calculate historical hit rate for a player on a specific stat type.
    
    Args:
        db: Database session
        player_name: Player's name
        stat_type: Stat type (PTS, REB, AST, etc.)
    
    Returns:
        Dictionary with hit rate statistics
    """
    result = await db.execute(
        select(PlayerStat)
        .where(
            and_(
                PlayerStat.player_name == player_name,
                PlayerStat.stat_type == stat_type,
            )
        )
        .order_by(PlayerStat.date.desc())
    )
    stats = result.scalars().all()
    
    if not stats:
        return {
            "player_name": player_name,
            "stat_type": stat_type,
            "total_picks": 0,
            "hits": 0,
            "misses": 0,
            "hit_rate": 0.0,
        }
    
    hits = sum(1 for s in stats if s.result == "hit")
    misses = sum(1 for s in stats if s.result == "miss")
    total = hits + misses
    
    return {
        "player_name": player_name,
        "stat_type": stat_type,
        "total_picks": total,
        "hits": hits,
        "misses": misses,
        "hit_rate": round(hits / total * 100, 2) if total > 0 else 0.0,
    }


async def get_recent_performance(
    db: AsyncSession,
    player_name: str,
    days: int = 14,
) -> list[dict[str, Any]]:
    """
    Get a player's recent performance over the last N days.
    
    Args:
        db: Database session
        player_name: Player's name
        days: Number of days to look back
    
    Returns:
        List of recent stat records
    """
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    
    result = await db.execute(
        select(PlayerStat)
        .where(
            and_(
                PlayerStat.player_name == player_name,
                PlayerStat.date >= cutoff,
            )
        )
        .order_by(PlayerStat.date.desc())
    )
    stats = result.scalars().all()
    
    return [
        {
            "id": s.id,
            "player_name": s.player_name,
            "team": s.team,
            "opponent": s.opponent,
            "date": s.date.isoformat(),
            "stat_type": s.stat_type,
            "actual_value": s.actual_value,
            "line": s.line,
            "result": s.result,
        }
        for s in stats
    ]


async def get_all_hit_rates(db: AsyncSession) -> list[dict[str, Any]]:
    """
    Get hit rates for all tracked player/stat combinations.
    
    Returns:
        List of hit rate records from HistoricalPerformance table
    """
    result = await db.execute(
        select(HistoricalPerformance)
        .order_by(HistoricalPerformance.hit_rate_percentage.desc())
    )
    performances = result.scalars().all()
    
    return [
        {
            "id": p.id,
            "player_name": p.player_name,
            "stat_type": p.stat_type,
            "total_picks": p.total_picks,
            "hits": p.hits,
            "misses": p.misses,
            "hit_rate_percentage": p.hit_rate_percentage,
            "avg_ev": p.avg_ev,
        }
        for p in performances
    ]


async def get_player_summary(
    db: AsyncSession,
    player_name: str,
) -> dict[str, Any]:
    """
    Get comprehensive player statistics summary.
    
    Args:
        db: Database session
        player_name: Player's name
    
    Returns:
        Dictionary with player's complete stats summary
    """
    # Get historical performance records
    perf_result = await db.execute(
        select(HistoricalPerformance)
        .where(HistoricalPerformance.player_name == player_name)
    )
    performances = perf_result.scalars().all()
    
    # Get recent stats
    recent_stats = await get_recent_performance(db, player_name, days=14)
    
    # Get picks for this player
    picks_result = await db.execute(
        select(Pick)
        .where(Pick.player_name == player_name)
        .order_by(Pick.created_at.desc())
        .limit(20)
    )
    picks = picks_result.scalars().all()
    
    # Calculate overall stats
    total_picks = sum(p.total_picks for p in performances)
    total_hits = sum(p.hits for p in performances)
    overall_hit_rate = round(total_hits / total_picks * 100, 2) if total_picks > 0 else 0.0
    avg_ev = round(sum(p.avg_ev for p in performances) / len(performances), 2) if performances else 0.0
    
    return {
        "player_name": player_name,
        "overall_stats": {
            "total_picks": total_picks,
            "total_hits": total_hits,
            "overall_hit_rate": overall_hit_rate,
            "avg_ev": avg_ev,
        },
        "by_stat_type": [
            {
                "stat_type": p.stat_type,
                "total_picks": p.total_picks,
                "hits": p.hits,
                "hit_rate": p.hit_rate_percentage,
                "avg_ev": p.avg_ev,
            }
            for p in performances
        ],
        "recent_performance": recent_stats[:10],
        "recent_picks": [
            {
                "id": p.id,
                "pick_type": p.pick_type,
                "stat_type": p.stat_type,
                "line": p.line,
                "odds": p.odds,
                "ev_percentage": p.ev_percentage,
                "confidence": p.confidence,
            }
            for p in picks
        ],
    }


# =============================================================================
# Real Analytics from PickResult Data
# =============================================================================

async def calculate_real_hit_rates(
    db: AsyncSession,
    player_id: int,
    stat_type: Optional[str] = None,
    games: int = 10,
) -> dict[str, Any]:
    """
    Calculate actual hit rates from settled PickResult data.
    
    Args:
        db: Database session
        player_id: Player's database ID
        stat_type: Optional stat type filter (PTS, REB, AST, etc.)
        games: Number of recent games to analyze
    
    Returns:
        Dictionary with actual hit rate statistics
    """
    # Build query for pick results
    query = (
        select(PickResult)
        .join(ModelPick, PickResult.pick_id == ModelPick.id)
        .where(PickResult.player_id == player_id)
        .order_by(desc(PickResult.settled_at))
        .limit(games)
    )
    
    result = await db.execute(query)
    results = result.scalars().all()
    
    if not results:
        return {
            "player_id": player_id,
            "total_settled": 0,
            "hits": 0,
            "misses": 0,
            "hit_rate": 0.0,
            "recent_games": games,
        }
    
    hits = sum(1 for r in results if r.hit)
    total = len(results)
    
    return {
        "player_id": player_id,
        "total_settled": total,
        "hits": hits,
        "misses": total - hits,
        "hit_rate": round(hits / total * 100, 2) if total > 0 else 0.0,
        "recent_games": games,
    }


async def calculate_ev_performance(
    db: AsyncSession,
    player_id: Optional[int] = None,
    days: int = 30,
) -> dict[str, Any]:
    """
    Calculate realized EV from settled picks.
    
    Compares predicted EV to actual returns over a period.
    
    Args:
        db: Database session
        player_id: Optional player filter
        days: Number of days to analyze
    
    Returns:
        EV performance statistics
    """
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    
    # Query settled picks with their results
    query = (
        select(ModelPick, PickResult)
        .join(PickResult, PickResult.pick_id == ModelPick.id)
        .where(PickResult.settled_at >= cutoff)
    )
    
    if player_id:
        query = query.where(ModelPick.player_id == player_id)
    
    result = await db.execute(query)
    picks_with_results = result.all()
    
    if not picks_with_results:
        return {
            "player_id": player_id,
            "days": days,
            "total_picks": 0,
            "predicted_ev_total": 0.0,
            "actual_return": 0.0,
            "ev_accuracy": 0.0,
        }
    
    total_predicted_ev = 0.0
    total_actual_return = 0.0
    
    for pick, pick_result in picks_with_results:
        total_predicted_ev += pick.expected_value
        
        # Calculate actual return
        if pick_result.hit:
            # Won: return = odds - 1 (for decimal odds)
            # For American odds, convert first
            if pick.odds > 0:
                decimal_odds = 1 + (pick.odds / 100)
            else:
                decimal_odds = 1 + (100 / abs(pick.odds))
            total_actual_return += decimal_odds - 1
        else:
            # Lost: return = -1 (lost the stake)
            total_actual_return -= 1
    
    total_picks = len(picks_with_results)
    
    return {
        "player_id": player_id,
        "days": days,
        "total_picks": total_picks,
        "predicted_ev_total": round(total_predicted_ev, 4),
        "actual_return": round(total_actual_return, 4),
        "predicted_ev_per_pick": round(total_predicted_ev / total_picks, 4) if total_picks > 0 else 0.0,
        "actual_return_per_pick": round(total_actual_return / total_picks, 4) if total_picks > 0 else 0.0,
        "ev_accuracy": round(
            (total_actual_return / total_predicted_ev) * 100, 2
        ) if total_predicted_ev != 0 else 0.0,
    }


async def calculate_odds_trends(
    db: AsyncSession,
    player_id: int,
    stat_type: Optional[str] = None,
    days: int = 7,
) -> dict[str, Any]:
    """
    Analyze odds movement trends from OddsSnapshot data.
    
    Identifies patterns like:
    - Opening vs closing line movement
    - Sharp money indicators
    - Line value opportunities
    
    Args:
        db: Database session
        player_id: Player's database ID
        stat_type: Optional stat type filter
        days: Days of history to analyze
    
    Returns:
        Trend analysis data
    """
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    
    # Get odds snapshots for this player
    query = (
        select(OddsSnapshot)
        .where(
            and_(
                OddsSnapshot.player_id == player_id,
                OddsSnapshot.snapshot_at >= cutoff,
            )
        )
        .order_by(OddsSnapshot.game_id, OddsSnapshot.snapshot_at)
    )
    
    result = await db.execute(query)
    snapshots = result.scalars().all()
    
    if not snapshots:
        return {
            "player_id": player_id,
            "days": days,
            "total_snapshots": 0,
            "games_tracked": 0,
            "avg_line_movement": 0.0,
            "trends": [],
        }
    
    # Group by game and analyze movement
    games_data: dict[int, list[OddsSnapshot]] = {}
    for snap in snapshots:
        if snap.game_id not in games_data:
            games_data[snap.game_id] = []
        games_data[snap.game_id].append(snap)
    
    trends = []
    total_movement = 0.0
    
    for game_id, game_snapshots in games_data.items():
        if len(game_snapshots) < 2:
            continue
        
        # Sort by time
        sorted_snaps = sorted(game_snapshots, key=lambda s: s.snapshot_at)
        opening = sorted_snaps[0]
        closing = sorted_snaps[-1]
        
        # Calculate line movement
        if opening.price and closing.price:
            movement = closing.price - opening.price
            total_movement += movement
            
            trends.append({
                "game_id": game_id,
                "opening_price": opening.price,
                "closing_price": closing.price,
                "movement": round(movement, 4),
                "movement_direction": "up" if movement > 0 else "down" if movement < 0 else "flat",
                "snapshots_count": len(game_snapshots),
            })
    
    return {
        "player_id": player_id,
        "days": days,
        "total_snapshots": len(snapshots),
        "games_tracked": len(games_data),
        "avg_line_movement": round(total_movement / len(trends), 4) if trends else 0.0,
        "trends": trends[-10:],  # Return last 10 trends
    }


async def get_analytics_dashboard(
    db: AsyncSession,
    sport_key: str = "basketball_nba",
    days: int = 30,
) -> dict[str, Any]:
    """
    Get comprehensive analytics dashboard data.
    
    Args:
        db: Database session
        sport_key: Sport identifier
        days: Days of history
    
    Returns:
        Dashboard with key analytics metrics
    """
    from app.models import Sport
    
    # Get sport
    sport_result = await db.execute(
        select(Sport).where(Sport.league_code == sport_key.split("_")[-1].upper())
    )
    sport = sport_result.scalar_one_or_none()
    
    if not sport:
        return {"error": f"Sport not found: {sport_key}"}
    
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    
    # Overall pick performance
    picks_query = (
        select(
            func.count(PickResult.id).label("total"),
            func.sum(func.cast(PickResult.hit, type_=func.INTEGER())).label("hits"),
        )
        .join(ModelPick, PickResult.pick_id == ModelPick.id)
        .where(
            and_(
                ModelPick.sport_id == sport.id,
                PickResult.settled_at >= cutoff,
            )
        )
    )
    
    picks_result = await db.execute(picks_query)
    picks_stats = picks_result.one_or_none()
    
    total_picks = picks_stats.total if picks_stats else 0
    total_hits = picks_stats.hits if picks_stats else 0
    
    # Top performing players
    top_players_query = (
        select(
            Player.id,
            Player.name,
            func.count(PickResult.id).label("total_picks"),
            func.sum(func.cast(PickResult.hit, type_=func.INTEGER())).label("hits"),
        )
        .join(PickResult, Player.id == PickResult.player_id)
        .join(ModelPick, PickResult.pick_id == ModelPick.id)
        .where(
            and_(
                ModelPick.sport_id == sport.id,
                PickResult.settled_at >= cutoff,
            )
        )
        .group_by(Player.id, Player.name)
        .having(func.count(PickResult.id) >= 5)
        .order_by(desc(func.sum(func.cast(PickResult.hit, type_=func.INTEGER())) / func.count(PickResult.id)))
        .limit(10)
    )
    
    top_players_result = await db.execute(top_players_query)
    top_players = [
        {
            "player_id": row.id,
            "player_name": row.name,
            "total_picks": row.total_picks,
            "hits": row.hits or 0,
            "hit_rate": round((row.hits or 0) / row.total_picks * 100, 2) if row.total_picks > 0 else 0,
        }
        for row in top_players_result.all()
    ]
    
    return {
        "sport": sport_key,
        "period_days": days,
        "overall": {
            "total_picks": total_picks,
            "total_hits": total_hits or 0,
            "hit_rate": round((total_hits or 0) / total_picks * 100, 2) if total_picks > 0 else 0,
        },
        "top_players": top_players,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
