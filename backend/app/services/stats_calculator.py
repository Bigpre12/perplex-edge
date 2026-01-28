"""Stats calculator service for historical performance analysis."""
import logging
from datetime import datetime, timezone, timedelta
from typing import Any, Optional

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import PlayerStat, HistoricalPerformance, Pick

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
