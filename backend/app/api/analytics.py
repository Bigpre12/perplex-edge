"""Analytics API endpoints for historical performance data."""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.stats_calculator import (
    calculate_real_hit_rates,
    calculate_ev_performance,
    calculate_odds_trends,
    get_analytics_dashboard,
)
from app.services.etl_historical import (
    sync_historical_odds,
    sync_game_results,
    settle_picks,
    run_full_historical_sync,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/analytics", tags=["Analytics"])


# =============================================================================
# Hit Rate Endpoints
# =============================================================================

@router.get("/hit-rates/{player_id}")
async def get_player_hit_rates(
    player_id: int,
    stat_type: Optional[str] = Query(None, description="Filter by stat type (PTS, REB, AST, etc.)"),
    games: int = Query(10, ge=1, le=100, description="Number of recent games to analyze"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get actual hit rates for a player from settled picks.
    
    Calculates hit rates based on real PickResult data.
    """
    try:
        result = await calculate_real_hit_rates(
            db,
            player_id=player_id,
            stat_type=stat_type,
            games=games,
        )
        return result
    except Exception as e:
        logger.error(f"Error fetching hit rates for player {player_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e)[:200])


# =============================================================================
# EV Performance Endpoints
# =============================================================================

@router.get("/ev-performance")
async def get_ev_performance(
    player_id: Optional[int] = Query(None, description="Optional player filter"),
    days: int = Query(30, ge=1, le=365, description="Days of history to analyze"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get realized EV performance from settled picks.
    
    Compares predicted EV vs actual returns over time.
    """
    try:
        result = await calculate_ev_performance(
            db,
            player_id=player_id,
            days=days,
        )
        return result
    except Exception as e:
        logger.error(f"Error calculating EV performance: {e}")
        raise HTTPException(status_code=500, detail=str(e)[:200])


# =============================================================================
# Trends Endpoints
# =============================================================================

@router.get("/trends/{player_id}")
async def get_odds_trends(
    player_id: int,
    stat_type: Optional[str] = Query(None, description="Filter by stat type"),
    days: int = Query(7, ge=1, le=30, description="Days of history to analyze"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get odds movement trends for a player.
    
    Analyzes historical odds data from OddsSnapshot to identify:
    - Opening vs closing line movements
    - Sharp money indicators
    - Line value opportunities
    """
    try:
        result = await calculate_odds_trends(
            db,
            player_id=player_id,
            stat_type=stat_type,
            days=days,
        )
        return result
    except Exception as e:
        logger.error(f"Error fetching trends for player {player_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e)[:200])


# =============================================================================
# Strategy Backtester Endpoint
# =============================================================================

@router.get("/backtest")
async def run_backtest(
    sport_id: Optional[int] = Query(None, description="Filter by sport"),
    stat_type: Optional[str] = Query(None, description="Filter by stat type (PTS, AST, REB, etc.)"),
    side: Optional[str] = Query(None, description="Filter by side (over/under)"),
    min_ev: float = Query(0.03, ge=0.0, le=0.30, description="Min EV threshold (0.03 = 3%)"),
    min_confidence: float = Query(0.55, ge=0.0, le=1.0, description="Min confidence threshold (0.55 = 55%)"),
    days_back: int = Query(30, ge=7, le=365, description="Days of history to analyze"),
    db: AsyncSession = Depends(get_db),
):
    """
    Run a strategy backtest simulation.
    
    Define simple rules (min EV, stat type, side) and see how that strategy
    would have performed over historical data.
    
    Example queries:
    - "How did NBA assists overs with 5%+ EV perform last 30 days?"
    - "What's the hit rate on NFL receiving yards under 3% EV?"
    
    Returns:
    - qualifying_bets: Number of bets matching the criteria
    - wins/losses: Record
    - hit_rate: Percentage of bets that hit
    - flat_stake_roi: ROI if betting 1 unit per bet
    - kelly_stake_roi: ROI using quarter-Kelly sizing
    - confidence_buckets: Hit rate breakdown by confidence level
    """
    from app.services.backtest_service import run_backtest as backtest
    from datetime import date, timedelta
    
    end_date = date.today()
    start_date = end_date - timedelta(days=days_back)
    
    try:
        result = await backtest(
            db,
            sport_id=sport_id,
            stat_type=stat_type,
            side=side,
            min_ev=min_ev,
            min_confidence=min_confidence,
            start_date=start_date,
            end_date=end_date,
        )
        return result
    except Exception as e:
        logger.error(f"Backtest error: {e}", exc_info=True)
        return {
            "qualifying_bets": 0,
            "wins": 0,
            "losses": 0,
            "hit_rate": 0.0,
            "flat_stake_roi": 0.0,
            "kelly_stake_roi": 0.0,
            "avg_ev": 0.0,
            "error": str(e)[:200],
            "sample_quality": "insufficient",
        }


# =============================================================================
# Market Performance Endpoint
# =============================================================================

@router.get("/market-performance")
async def get_market_performance(
    days: int = Query(30, ge=1, le=365, description="Days of history to analyze"),
    sport_id: Optional[int] = Query(None, description="Optional sport filter"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get CLV/ROI performance broken down by market type.
    
    Returns metrics for each market (PTS, AST, REB, spreads, etc.):
    - Total bets and sample size
    - Win rate and ROI
    - CLV stats (avg CLV, beat-close percentage)
    - Model accuracy (predicted vs actual hit rate)
    
    Use this to identify which markets the model performs best in.
    """
    from datetime import datetime, timedelta, timezone
    from sqlalchemy import select, func, case, and_
    from app.models import UserBet, PickResult
    from app.models.bet import BetStatus
    
    cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=days)
    
    # Base filter
    conditions = [UserBet.created_at >= cutoff]
    if sport_id:
        conditions.append(UserBet.sport_id == sport_id)
    base_filter = and_(*conditions)
    
    # Get ROI/CLV by market type
    settled_filter = and_(base_filter, UserBet.status != BetStatus.PENDING)
    
    result = await db.execute(
        select(
            UserBet.market_type,
            func.count(UserBet.id).label('total_bets'),
            func.sum(case((UserBet.status == BetStatus.WON, 1), else_=0)).label('won'),
            func.sum(case((UserBet.status == BetStatus.LOST, 1), else_=0)).label('lost'),
            func.sum(UserBet.stake).label('total_stake'),
            func.sum(UserBet.profit_loss).label('total_pl'),
            func.avg(UserBet.clv_cents).label('avg_clv'),
            func.sum(case((UserBet.clv_cents > 0, 1), else_=0)).label('positive_clv_count'),
            func.count(UserBet.clv_cents).label('clv_count'),
        )
        .where(settled_filter)
        .group_by(UserBet.market_type)
        .order_by(func.sum(UserBet.profit_loss).desc())
    )
    
    markets = []
    for row in result.all():
        market_type, total, won, lost, stake, pl, avg_clv, pos_clv, clv_count = row
        
        win_rate = won / (won + lost) if (won + lost) > 0 else 0.0
        roi = (pl / stake * 100) if stake and stake > 0 else 0.0
        beat_close_pct = (pos_clv / clv_count * 100) if clv_count and clv_count > 0 else 0.0
        
        markets.append({
            "market_type": market_type or "unknown",
            "total_bets": total,
            "won": won or 0,
            "lost": lost or 0,
            "win_rate": round(win_rate * 100, 1),
            "total_stake": round(stake or 0, 2),
            "total_profit_loss": round(pl or 0, 2),
            "roi": round(roi, 2),
            "avg_clv_cents": round(avg_clv or 0, 2),
            "beat_close_pct": round(beat_close_pct, 1),
            "sample_quality": "high" if total >= 50 else "medium" if total >= 20 else "low",
        })
    
    # Calculate totals
    total_bets = sum(m["total_bets"] for m in markets)
    total_pl = sum(m["total_profit_loss"] for m in markets)
    total_stake = sum(m["total_stake"] for m in markets)
    
    return {
        "markets": markets,
        "summary": {
            "total_bets": total_bets,
            "total_profit_loss": round(total_pl, 2),
            "overall_roi": round((total_pl / total_stake * 100) if total_stake > 0 else 0, 2),
            "best_market": markets[0]["market_type"] if markets else None,
            "worst_market": markets[-1]["market_type"] if markets else None,
        },
        "filters": {
            "days": days,
            "sport_id": sport_id,
        },
    }


# =============================================================================
# Dashboard Endpoint
# =============================================================================

@router.get("/dashboard")
async def get_dashboard(
    sport: str = Query("nba", description="Sport: nba, nfl, mlb, nhl"),
    days: int = Query(30, ge=1, le=365, description="Days of history"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get comprehensive analytics dashboard.
    
    Returns:
    - Overall pick performance
    - Top performing players
    - Key metrics summary
    """
    sport_key_map = {
        "nba": "basketball_nba",
        "nfl": "americanfootball_nfl",
        "mlb": "baseball_mlb",
        "nhl": "icehockey_nhl",
    }
    
    sport_key = sport_key_map.get(sport.lower())
    if not sport_key:
        raise HTTPException(status_code=400, detail=f"Unknown sport: {sport}")
    
    try:
        result = await get_analytics_dashboard(
            db,
            sport_key=sport_key,
            days=days,
        )
        return result
    except Exception as e:
        logger.error(f"Error fetching dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e)[:200])


# =============================================================================
# Sync Endpoints (Manual Triggers)
# =============================================================================

@router.post("/sync")
async def trigger_historical_sync(
    sport: str = Query("nba", description="Sport to sync"),
    db: AsyncSession = Depends(get_db),
):
    """
    Trigger manual historical data sync from OddsPapi.
    
    Syncs:
    1. Historical odds movements
    2. Game results/scores
    3. Pick settlements
    
    Note: Requires ODDSPAPI_API_KEY to be configured.
    """
    from app.core.config import get_settings
    
    settings = get_settings()
    if not settings.oddspapi_api_key:
        raise HTTPException(
            status_code=400,
            detail="OddsPapi API key not configured. Set ODDSPAPI_API_KEY environment variable."
        )
    
    sport_key_map = {
        "nba": "basketball_nba",
        "nfl": "americanfootball_nfl",
        "mlb": "baseball_mlb",
        "nhl": "icehockey_nhl",
    }
    
    sport_key = sport_key_map.get(sport.lower())
    if not sport_key:
        raise HTTPException(status_code=400, detail=f"Unknown sport: {sport}")
    
    try:
        result = await run_full_historical_sync(db, sport_key)
        return {
            "status": "success",
            "sport": sport,
            "results": result,
        }
    except Exception as e:
        logger.error(f"Error running historical sync: {e}")
        raise HTTPException(status_code=500, detail=str(e)[:200])


@router.post("/sync/odds")
async def trigger_historical_odds_sync(
    sport: str = Query("nba", description="Sport to sync"),
    days_back: int = Query(7, ge=1, le=30, description="Days of history to fetch"),
    db: AsyncSession = Depends(get_db),
):
    """
    Sync historical odds only (without results/settlements).
    """
    from app.core.config import get_settings
    
    settings = get_settings()
    if not settings.oddspapi_api_key:
        raise HTTPException(
            status_code=400,
            detail="OddsPapi API key not configured"
        )
    
    sport_key_map = {
        "nba": "basketball_nba",
        "nfl": "americanfootball_nfl",
    }
    
    sport_key = sport_key_map.get(sport.lower())
    if not sport_key:
        raise HTTPException(status_code=400, detail=f"Unknown sport: {sport}")
    
    try:
        result = await sync_historical_odds(db, sport_key, days_back)
        return {
            "status": "success",
            "sport": sport,
            "days_back": days_back,
            "result": result,
        }
    except Exception as e:
        logger.error(f"Error syncing historical odds: {e}")
        raise HTTPException(status_code=500, detail=str(e)[:200])


@router.post("/sync/results")
async def trigger_results_sync(
    sport: str = Query("nba", description="Sport to sync"),
    days_back: int = Query(3, ge=1, le=14, description="Days of games to check"),
    db: AsyncSession = Depends(get_db),
):
    """
    Sync game results and settle picks.
    """
    from app.core.config import get_settings
    
    settings = get_settings()
    if not settings.oddspapi_api_key:
        raise HTTPException(
            status_code=400,
            detail="OddsPapi API key not configured"
        )
    
    sport_key_map = {
        "nba": "basketball_nba",
        "nfl": "americanfootball_nfl",
    }
    
    sport_key = sport_key_map.get(sport.lower())
    if not sport_key:
        raise HTTPException(status_code=400, detail=f"Unknown sport: {sport}")
    
    try:
        # Sync results
        results_sync = await sync_game_results(db, sport_key, days_back)
        
        # Settle picks
        settlement = await settle_picks(db, sport_key)
        
        return {
            "status": "success",
            "sport": sport,
            "results_sync": results_sync,
            "settlement": settlement,
        }
    except Exception as e:
        logger.error(f"Error syncing results: {e}")
        raise HTTPException(status_code=500, detail=str(e)[:200])
