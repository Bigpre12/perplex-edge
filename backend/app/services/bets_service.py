"""Service for managing personal bet tracking and ROI analysis."""

import logging
from datetime import datetime, timezone, timedelta
from typing import Any, Optional, List
from collections import defaultdict

from pydantic import BaseModel
from sqlalchemy import select, func, and_, case
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import UserBet, BetStatus, Sport, Game, Player, ModelPick
from app.schemas.bets import (
    BetCreate,
    BetSettle,
    BetFilters,
    BetResponse,
    BetList,
    BetStatsResponse,
    ROIByCategory,
    CLVStats,
    CLVHistoryPoint,
    CLVHistoryResponse,
    QuickBetFromPick,
)

logger = logging.getLogger(__name__)


# =============================================================================
# Bet CRUD Operations
# =============================================================================

async def create_bet(db: AsyncSession, bet_data: BetCreate) -> UserBet:
    """Create a new bet record."""
    
    bet = UserBet(
        sport_id=bet_data.sport_id,
        game_id=bet_data.game_id,
        player_id=bet_data.player_id,
        market_type=bet_data.market_type,
        side=bet_data.side,
        line_value=bet_data.line_value,
        sportsbook=bet_data.sportsbook,
        opening_odds=bet_data.opening_odds,
        stake=bet_data.stake,
        status=BetStatus.PENDING,
        notes=bet_data.notes,
        model_pick_id=bet_data.model_pick_id,
        placed_at=bet_data.placed_at or datetime.now(timezone.utc).replace(tzinfo=None),
    )
    
    db.add(bet)
    await db.commit()
    await db.refresh(bet)
    
    logger.info(f"Created bet {bet.id}: {bet.market_type} {bet.side} @ {bet.opening_odds}")
    return bet


async def create_bet_from_pick(
    db: AsyncSession, 
    data: QuickBetFromPick,
) -> UserBet:
    """
    Quick-log a bet from a model pick.
    
    Copies the pick details and creates a bet record.
    """
    # Get the pick
    pick = await db.get(ModelPick, data.pick_id)
    if not pick:
        raise ValueError(f"Pick {data.pick_id} not found")
    
    # Get player name if it's a prop
    player_id = pick.player_id
    
    # Get market type from the pick's market
    market_result = await db.execute(
        select(Market).where(Market.id == pick.market_id)
    )
    market = market_result.scalar_one_or_none()
    market_type = market.market_type if market else "unknown"
    
    bet = UserBet(
        sport_id=pick.sport_id,
        game_id=pick.game_id,
        player_id=player_id,
        market_type=market_type,
        side=pick.side,
        line_value=pick.line_value,
        sportsbook=data.sportsbook,
        opening_odds=data.actual_odds or int(pick.odds),
        stake=data.stake,
        status=BetStatus.PENDING,
        notes=data.notes,
        model_pick_id=data.pick_id,
        placed_at=datetime.now(timezone.utc).replace(tzinfo=None),
    )
    
    db.add(bet)
    await db.commit()
    await db.refresh(bet)
    
    logger.info(f"Created bet {bet.id} from pick {data.pick_id}")
    return bet


async def get_bet(db: AsyncSession, bet_id: int) -> Optional[UserBet]:
    """Get a single bet by ID."""
    return await db.get(UserBet, bet_id)


async def list_bets(
    db: AsyncSession,
    filters: BetFilters,
) -> BetList:
    """List bets with filtering and pagination."""
    
    # Build base query
    query = select(UserBet)
    count_query = select(func.count(UserBet.id))
    
    # Apply filters
    conditions = []
    
    if filters.sport_id:
        conditions.append(UserBet.sport_id == filters.sport_id)
    
    if filters.sportsbook:
        conditions.append(UserBet.sportsbook == filters.sportsbook)
    
    if filters.market_type:
        conditions.append(UserBet.market_type == filters.market_type)
    
    if filters.status:
        conditions.append(UserBet.status == filters.status)
    
    if filters.player_id:
        conditions.append(UserBet.player_id == filters.player_id)
    
    if filters.date_from:
        conditions.append(UserBet.placed_at >= filters.date_from)
    
    if filters.date_to:
        conditions.append(UserBet.placed_at <= filters.date_to)
    
    if filters.min_stake:
        conditions.append(UserBet.stake >= filters.min_stake)
    
    if filters.max_stake:
        conditions.append(UserBet.stake <= filters.max_stake)
    
    if conditions:
        query = query.where(and_(*conditions))
        count_query = count_query.where(and_(*conditions))
    
    # Get total count
    total = await db.scalar(count_query) or 0
    
    # Apply pagination and ordering
    offset = (filters.page - 1) * filters.page_size
    query = query.order_by(UserBet.placed_at.desc())
    query = query.offset(offset).limit(filters.page_size)
    
    # Execute
    result = await db.execute(query)
    bets = result.scalars().all()
    
    # Build response items with sport/player names
    items = []
    for bet in bets:
        # Get sport name
        sport = await db.get(Sport, bet.sport_id)
        sport_name = sport.name if sport else None
        
        # Get player name if applicable
        player_name = None
        if bet.player_id:
            player = await db.get(Player, bet.player_id)
            player_name = player.name if player else None
        
        items.append(BetResponse(
            id=bet.id,
            sport_id=bet.sport_id,
            sport_name=sport_name,
            game_id=bet.game_id,
            player_id=bet.player_id,
            player_name=player_name,
            market_type=bet.market_type,
            side=bet.side,
            line_value=bet.line_value,
            sportsbook=bet.sportsbook,
            opening_odds=bet.opening_odds,
            stake=bet.stake,
            status=bet.status.value,
            actual_value=bet.actual_value,
            closing_odds=bet.closing_odds,
            closing_line=bet.closing_line,
            clv_cents=bet.clv_cents,
            profit_loss=bet.profit_loss,
            placed_at=bet.placed_at,
            settled_at=bet.settled_at,
            notes=bet.notes,
            model_pick_id=bet.model_pick_id,
            created_at=bet.created_at,
            updated_at=bet.updated_at,
        ))
    
    total_pages = (total + filters.page_size - 1) // filters.page_size
    
    return BetList(
        items=items,
        total=total,
        page=filters.page,
        page_size=filters.page_size,
        total_pages=total_pages,
    )


async def settle_bet(
    db: AsyncSession,
    bet_id: int,
    settle_data: BetSettle,
) -> UserBet:
    """Settle a bet with result."""
    
    bet = await db.get(UserBet, bet_id)
    if not bet:
        raise ValueError(f"Bet {bet_id} not found")
    
    if bet.status != BetStatus.PENDING:
        raise ValueError(f"Bet {bet_id} is already settled with status {bet.status}")
    
    # Update status
    bet.status = BetStatus(settle_data.status.value)
    bet.settled_at = datetime.now(timezone.utc).replace(tzinfo=None)
    
    # Set result details
    if settle_data.actual_value is not None:
        bet.actual_value = settle_data.actual_value
    
    if settle_data.closing_odds is not None:
        bet.closing_odds = settle_data.closing_odds
    
    if settle_data.closing_line is not None:
        bet.closing_line = settle_data.closing_line
    
    # Calculate CLV
    bet.clv_cents = bet.calculate_clv()
    
    # Calculate P/L
    bet.profit_loss = bet.calculate_profit_loss()
    
    await db.commit()
    await db.refresh(bet)
    
    logger.info(
        f"Settled bet {bet.id}: {bet.status.value}, P/L={bet.profit_loss}, CLV={bet.clv_cents}"
    )
    return bet


async def delete_bet(db: AsyncSession, bet_id: int) -> bool:
    """Delete a bet record."""
    
    bet = await db.get(UserBet, bet_id)
    if not bet:
        return False
    
    await db.delete(bet)
    await db.commit()
    
    logger.info(f"Deleted bet {bet_id}")
    return True


# =============================================================================
# Statistics Calculations
# =============================================================================

async def get_bet_stats(
    db: AsyncSession,
    sport_id: Optional[int] = None,
    days_back: Optional[int] = None,
) -> BetStatsResponse:
    """
    Calculate comprehensive betting statistics.
    
    Args:
        db: Database session
        sport_id: Optional filter by sport
        days_back: Optional filter to last N days
    """
    
    # Build base filter conditions
    conditions = []
    if sport_id:
        conditions.append(UserBet.sport_id == sport_id)
    if days_back:
        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=days_back)
        conditions.append(UserBet.placed_at >= cutoff)
    
    base_filter = and_(*conditions) if conditions else True
    
    # Get total counts
    total_bets = await db.scalar(
        select(func.count(UserBet.id)).where(base_filter)
    ) or 0
    
    pending_bets = await db.scalar(
        select(func.count(UserBet.id)).where(
            and_(base_filter, UserBet.status == BetStatus.PENDING)
        )
    ) or 0
    
    settled_bets = total_bets - pending_bets
    
    # Get status breakdown for settled bets
    settled_filter = and_(base_filter, UserBet.status != BetStatus.PENDING)
    
    won = await db.scalar(
        select(func.count(UserBet.id)).where(
            and_(base_filter, UserBet.status == BetStatus.WON)
        )
    ) or 0
    
    lost = await db.scalar(
        select(func.count(UserBet.id)).where(
            and_(base_filter, UserBet.status == BetStatus.LOST)
        )
    ) or 0
    
    pushed = await db.scalar(
        select(func.count(UserBet.id)).where(
            and_(base_filter, UserBet.status == BetStatus.PUSH)
        )
    ) or 0
    
    voided = await db.scalar(
        select(func.count(UserBet.id)).where(
            and_(base_filter, UserBet.status == BetStatus.VOID)
        )
    ) or 0
    
    # Calculate totals
    total_stake = await db.scalar(
        select(func.sum(UserBet.stake)).where(settled_filter)
    ) or 0.0
    
    total_profit_loss = await db.scalar(
        select(func.sum(UserBet.profit_loss)).where(settled_filter)
    ) or 0.0
    
    # Calculate ROI and win rate
    overall_roi = (total_profit_loss / total_stake * 100) if total_stake > 0 else 0.0
    overall_win_rate = (won / (won + lost)) if (won + lost) > 0 else 0.0
    
    # CLV stats
    clv_stats = await _calculate_clv_stats(db, base_filter)
    
    # ROI by market
    by_market = await _roi_by_category(db, base_filter, UserBet.market_type)
    
    # ROI by sportsbook
    by_sportsbook = await _roi_by_category(db, base_filter, UserBet.sportsbook)
    
    # ROI by sport
    by_sport = await _roi_by_sport(db, base_filter)
    
    # Top/worst players
    top_players, worst_players = await _roi_by_player(db, base_filter, min_bets=5)
    
    return BetStatsResponse(
        total_bets=total_bets,
        settled_bets=settled_bets,
        pending_bets=pending_bets,
        total_stake=round(total_stake, 2),
        total_profit_loss=round(total_profit_loss, 2),
        overall_roi=round(overall_roi, 2),
        overall_win_rate=round(overall_win_rate, 4),
        won=won,
        lost=lost,
        pushed=pushed,
        voided=voided,
        clv_stats=clv_stats,
        by_market=by_market,
        by_sportsbook=by_sportsbook,
        by_sport=by_sport,
        top_players=top_players,
        worst_players=worst_players,
    )


async def _calculate_clv_stats(db: AsyncSession, base_filter) -> CLVStats:
    """Calculate CLV statistics."""
    
    # Filter to bets with CLV data
    clv_filter = and_(base_filter, UserBet.clv_cents.isnot(None))
    
    total_with_clv = await db.scalar(
        select(func.count(UserBet.id)).where(clv_filter)
    ) or 0
    
    if total_with_clv == 0:
        return CLVStats(
            total_bets_with_clv=0,
            avg_clv_cents=0.0,
            positive_clv_count=0,
            positive_clv_pct=0.0,
            total_clv_cents=0.0,
        )
    
    avg_clv = await db.scalar(
        select(func.avg(UserBet.clv_cents)).where(clv_filter)
    ) or 0.0
    
    total_clv = await db.scalar(
        select(func.sum(UserBet.clv_cents)).where(clv_filter)
    ) or 0.0
    
    positive_count = await db.scalar(
        select(func.count(UserBet.id)).where(
            and_(clv_filter, UserBet.clv_cents > 0)
        )
    ) or 0
    
    return CLVStats(
        total_bets_with_clv=total_with_clv,
        avg_clv_cents=round(avg_clv, 2),
        positive_clv_count=positive_count,
        positive_clv_pct=round(positive_count / total_with_clv, 4) if total_with_clv > 0 else 0.0,
        total_clv_cents=round(total_clv, 2),
    )


async def _roi_by_category(
    db: AsyncSession, 
    base_filter, 
    category_column,
) -> list[ROIByCategory]:
    """Calculate ROI grouped by a category column."""
    
    settled_filter = and_(base_filter, UserBet.status != BetStatus.PENDING)
    
    result = await db.execute(
        select(
            category_column,
            func.count(UserBet.id).label('total_bets'),
            func.sum(case((UserBet.status == BetStatus.WON, 1), else_=0)).label('won'),
            func.sum(case((UserBet.status == BetStatus.LOST, 1), else_=0)).label('lost'),
            func.sum(case((UserBet.status == BetStatus.PUSH, 1), else_=0)).label('pushed'),
            func.sum(UserBet.stake).label('total_stake'),
            func.sum(UserBet.profit_loss).label('total_pl'),
        )
        .where(settled_filter)
        .group_by(category_column)
        .order_by(func.sum(UserBet.profit_loss).desc())
    )
    
    categories = []
    for row in result.all():
        category, total, won, lost, pushed, stake, pl = row
        win_rate = won / (won + lost) if (won + lost) > 0 else 0.0
        roi = (pl / stake * 100) if stake > 0 else 0.0
        
        categories.append(ROIByCategory(
            category=category,
            total_bets=total,
            won=won,
            lost=lost,
            pushed=pushed,
            win_rate=round(win_rate, 4),
            total_stake=round(stake, 2),
            total_profit_loss=round(pl or 0, 2),
            roi=round(roi, 2),
        ))
    
    return categories


async def _roi_by_sport(db: AsyncSession, base_filter) -> list[ROIByCategory]:
    """Calculate ROI grouped by sport with sport names."""
    
    settled_filter = and_(base_filter, UserBet.status != BetStatus.PENDING)
    
    result = await db.execute(
        select(
            Sport.name,
            func.count(UserBet.id).label('total_bets'),
            func.sum(case((UserBet.status == BetStatus.WON, 1), else_=0)).label('won'),
            func.sum(case((UserBet.status == BetStatus.LOST, 1), else_=0)).label('lost'),
            func.sum(case((UserBet.status == BetStatus.PUSH, 1), else_=0)).label('pushed'),
            func.sum(UserBet.stake).label('total_stake'),
            func.sum(UserBet.profit_loss).label('total_pl'),
        )
        .join(Sport, UserBet.sport_id == Sport.id)
        .where(settled_filter)
        .group_by(Sport.name)
        .order_by(func.sum(UserBet.profit_loss).desc())
    )
    
    categories = []
    for row in result.all():
        name, total, won, lost, pushed, stake, pl = row
        win_rate = won / (won + lost) if (won + lost) > 0 else 0.0
        roi = (pl / stake * 100) if stake > 0 else 0.0
        
        categories.append(ROIByCategory(
            category=name,
            total_bets=total,
            won=won,
            lost=lost,
            pushed=pushed,
            win_rate=round(win_rate, 4),
            total_stake=round(stake, 2),
            total_profit_loss=round(pl or 0, 2),
            roi=round(roi, 2),
        ))
    
    return categories


async def _roi_by_player(
    db: AsyncSession, 
    base_filter,
    min_bets: int = 5,
) -> tuple[list[ROIByCategory], list[ROIByCategory]]:
    """Calculate ROI by player, returning top and worst performers."""
    
    settled_filter = and_(
        base_filter, 
        UserBet.status != BetStatus.PENDING,
        UserBet.player_id.isnot(None),
    )
    
    result = await db.execute(
        select(
            Player.name,
            func.count(UserBet.id).label('total_bets'),
            func.sum(case((UserBet.status == BetStatus.WON, 1), else_=0)).label('won'),
            func.sum(case((UserBet.status == BetStatus.LOST, 1), else_=0)).label('lost'),
            func.sum(case((UserBet.status == BetStatus.PUSH, 1), else_=0)).label('pushed'),
            func.sum(UserBet.stake).label('total_stake'),
            func.sum(UserBet.profit_loss).label('total_pl'),
        )
        .join(Player, UserBet.player_id == Player.id)
        .where(settled_filter)
        .group_by(Player.name)
        .having(func.count(UserBet.id) >= min_bets)
    )
    
    all_players = []
    for row in result.all():
        name, total, won, lost, pushed, stake, pl = row
        win_rate = won / (won + lost) if (won + lost) > 0 else 0.0
        roi = (pl / stake * 100) if stake > 0 else 0.0
        
        all_players.append(ROIByCategory(
            category=name,
            total_bets=total,
            won=won,
            lost=lost,
            pushed=pushed,
            win_rate=round(win_rate, 4),
            total_stake=round(stake, 2),
            total_profit_loss=round(pl or 0, 2),
            roi=round(roi, 2),
        ))
    
    # Sort by ROI
    all_players.sort(key=lambda x: x.roi, reverse=True)
    
    top_players = all_players[:10]
    worst_players = all_players[-10:][::-1] if len(all_players) >= 10 else all_players[::-1]
    
    return top_players, worst_players


async def get_clv_history(
    db: AsyncSession,
    sport_id: Optional[int] = None,
    days_back: int = 30,
) -> CLVHistoryResponse:
    """Get CLV history for charting."""
    
    cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=days_back)
    
    conditions = [
        UserBet.clv_cents.isnot(None),
        UserBet.settled_at >= cutoff,
    ]
    if sport_id:
        conditions.append(UserBet.sport_id == sport_id)
    
    # Get all bets with CLV, ordered by date
    result = await db.execute(
        select(UserBet.settled_at, UserBet.clv_cents)
        .where(and_(*conditions))
        .order_by(UserBet.settled_at)
    )
    
    bets = result.all()
    
    if not bets:
        return CLVHistoryResponse(
            data_points=[],
            total_clv=0.0,
            avg_clv=0.0,
        )
    
    # Group by date and calculate cumulative
    daily_data = defaultdict(lambda: {"clv_sum": 0.0, "count": 0})
    
    for settled_at, clv in bets:
        date_str = settled_at.strftime("%Y-%m-%d")
        daily_data[date_str]["clv_sum"] += clv
        daily_data[date_str]["count"] += 1
    
    # Build data points with cumulative
    data_points = []
    cumulative = 0.0
    
    for date_str in sorted(daily_data.keys()):
        day = daily_data[date_str]
        cumulative += day["clv_sum"]
        
        data_points.append(CLVHistoryPoint(
            date=date_str,
            cumulative_clv=round(cumulative, 2),
            rolling_clv_7d=None,  # Could calculate 7-day rolling average
            bet_count=day["count"],
        ))
    
    total_clv = sum(bet[1] for bet in bets)
    avg_clv = total_clv / len(bets) if bets else 0.0
    
    return CLVHistoryResponse(
        data_points=data_points,
        total_clv=round(total_clv, 2),
        avg_clv=round(avg_clv, 2),
    )


# =============================================================================
# Session Report (ROI/CLV by Market/Book over Date Range)
# =============================================================================

class SessionMetric(BaseModel):
    """Metrics for a single category in session report."""
    name: str
    total_bets: int
    settled_bets: int
    won: int
    lost: int
    pushed: int
    win_rate: float
    total_staked: float
    total_profit_loss: float
    roi_pct: float
    avg_clv: float
    positive_clv_pct: float  # % of bets that beat the closing line


class SessionReportResponse(BaseModel):
    """Comprehensive session report."""
    
    # Summary
    date_from: datetime
    date_to: datetime
    total_days: int
    
    # Overall stats
    total_bets: int
    settled_bets: int
    pending_bets: int
    overall_roi: float
    overall_win_rate: float
    total_profit_loss: float
    total_staked: float
    
    # CLV summary
    total_clv: float
    avg_clv: float
    positive_clv_pct: float
    
    # Breakdowns
    by_market: list[SessionMetric]
    by_sportsbook: list[SessionMetric]
    by_sport: list[SessionMetric]
    
    # Daily P/L curve
    daily_pl: list[dict]


async def get_session_report(
    db: AsyncSession,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    sport_id: Optional[int] = None,
) -> SessionReportResponse:
    """
    Generate comprehensive session report with ROI/CLV breakdown.
    
    Args:
        db: Database session
        date_from: Start date (defaults to 30 days ago)
        date_to: End date (defaults to now)
        sport_id: Optional filter by sport
    
    Returns:
        SessionReportResponse with full breakdown by market, book, sport
    """
    # Set date defaults
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    if date_to is None:
        date_to = now
    if date_from is None:
        date_from = now - timedelta(days=30)
    
    total_days = (date_to - date_from).days + 1
    
    # Build base filter
    conditions = [
        UserBet.placed_at >= date_from,
        UserBet.placed_at <= date_to,
    ]
    if sport_id:
        conditions.append(UserBet.sport_id == sport_id)
    
    base_filter = and_(*conditions)
    settled_filter = and_(base_filter, UserBet.status != BetStatus.PENDING)
    
    # Overall counts
    total_bets = await db.scalar(
        select(func.count(UserBet.id)).where(base_filter)
    ) or 0
    
    pending_bets = await db.scalar(
        select(func.count(UserBet.id)).where(
            and_(base_filter, UserBet.status == BetStatus.PENDING)
        )
    ) or 0
    
    settled_bets = total_bets - pending_bets
    
    # Overall record
    won = await db.scalar(
        select(func.count(UserBet.id)).where(
            and_(base_filter, UserBet.status == BetStatus.WON)
        )
    ) or 0
    
    lost = await db.scalar(
        select(func.count(UserBet.id)).where(
            and_(base_filter, UserBet.status == BetStatus.LOST)
        )
    ) or 0
    
    # Overall financials
    total_staked = await db.scalar(
        select(func.sum(UserBet.stake)).where(settled_filter)
    ) or 0.0
    
    total_profit_loss = await db.scalar(
        select(func.sum(UserBet.profit_loss)).where(settled_filter)
    ) or 0.0
    
    overall_roi = (total_profit_loss / total_staked * 100) if total_staked > 0 else 0.0
    overall_win_rate = (won / (won + lost)) if (won + lost) > 0 else 0.0
    
    # CLV summary
    total_clv = await db.scalar(
        select(func.sum(UserBet.clv_cents)).where(
            and_(settled_filter, UserBet.clv_cents.isnot(None))
        )
    ) or 0.0
    
    clv_count = await db.scalar(
        select(func.count(UserBet.id)).where(
            and_(settled_filter, UserBet.clv_cents.isnot(None))
        )
    ) or 0
    
    positive_clv_count = await db.scalar(
        select(func.count(UserBet.id)).where(
            and_(settled_filter, UserBet.clv_cents > 0)
        )
    ) or 0
    
    avg_clv = (total_clv / clv_count) if clv_count > 0 else 0.0
    positive_clv_pct = (positive_clv_count / clv_count * 100) if clv_count > 0 else 0.0
    
    # Helper to build SessionMetric from query result
    async def _build_metrics(group_column, group_name_fn=lambda x: x) -> list[SessionMetric]:
        result = await db.execute(
            select(
                group_column,
                func.count(UserBet.id).label('total'),
                func.sum(case((UserBet.status == BetStatus.PENDING, 0), else_=1)).label('settled'),
                func.sum(case((UserBet.status == BetStatus.WON, 1), else_=0)).label('won'),
                func.sum(case((UserBet.status == BetStatus.LOST, 1), else_=0)).label('lost'),
                func.sum(case((UserBet.status == BetStatus.PUSH, 1), else_=0)).label('pushed'),
                func.sum(UserBet.stake).label('staked'),
                func.sum(UserBet.profit_loss).label('pl'),
                func.avg(UserBet.clv_cents).label('avg_clv'),
                func.sum(case((UserBet.clv_cents > 0, 1), else_=0)).label('pos_clv'),
            )
            .where(base_filter)
            .group_by(group_column)
            .order_by(func.sum(UserBet.profit_loss).desc().nullslast())
        )
        
        metrics = []
        for row in result.all():
            name, total, settled, w, l, p, staked, pl, avg_c, pos_c = row
            if name is None:
                continue
            
            win_rate = w / (w + l) if (w + l) > 0 else 0.0
            roi = (pl / staked * 100) if staked and staked > 0 else 0.0
            pos_pct = (pos_c / settled * 100) if settled > 0 else 0.0
            
            metrics.append(SessionMetric(
                name=group_name_fn(name),
                total_bets=total,
                settled_bets=settled or 0,
                won=w or 0,
                lost=l or 0,
                pushed=p or 0,
                win_rate=round(win_rate, 4),
                total_staked=round(staked or 0, 2),
                total_profit_loss=round(pl or 0, 2),
                roi_pct=round(roi, 2),
                avg_clv=round(avg_c or 0, 2),
                positive_clv_pct=round(pos_pct, 2),
            ))
        
        return metrics
    
    # Breakdowns
    by_market = await _build_metrics(UserBet.market_type)
    by_sportsbook = await _build_metrics(UserBet.sportsbook)
    
    # By sport (need join)
    sport_result = await db.execute(
        select(
            Sport.name,
            func.count(UserBet.id).label('total'),
            func.sum(case((UserBet.status == BetStatus.PENDING, 0), else_=1)).label('settled'),
            func.sum(case((UserBet.status == BetStatus.WON, 1), else_=0)).label('won'),
            func.sum(case((UserBet.status == BetStatus.LOST, 1), else_=0)).label('lost'),
            func.sum(case((UserBet.status == BetStatus.PUSH, 1), else_=0)).label('pushed'),
            func.sum(UserBet.stake).label('staked'),
            func.sum(UserBet.profit_loss).label('pl'),
            func.avg(UserBet.clv_cents).label('avg_clv'),
            func.sum(case((UserBet.clv_cents > 0, 1), else_=0)).label('pos_clv'),
        )
        .join(Sport, UserBet.sport_id == Sport.id)
        .where(base_filter)
        .group_by(Sport.name)
        .order_by(func.sum(UserBet.profit_loss).desc().nullslast())
    )
    
    by_sport = []
    for row in sport_result.all():
        name, total, settled, w, l, p, staked, pl, avg_c, pos_c = row
        win_rate = w / (w + l) if (w + l) > 0 else 0.0
        roi = (pl / staked * 100) if staked and staked > 0 else 0.0
        pos_pct = (pos_c / settled * 100) if settled > 0 else 0.0
        
        by_sport.append(SessionMetric(
            name=name,
            total_bets=total,
            settled_bets=settled or 0,
            won=w or 0,
            lost=l or 0,
            pushed=p or 0,
            win_rate=round(win_rate, 4),
            total_staked=round(staked or 0, 2),
            total_profit_loss=round(pl or 0, 2),
            roi_pct=round(roi, 2),
            avg_clv=round(avg_c or 0, 2),
            positive_clv_pct=round(pos_pct, 2),
        ))
    
    # Daily P/L
    daily_result = await db.execute(
        select(
            func.date(UserBet.settled_at).label('date'),
            func.sum(UserBet.profit_loss).label('pl'),
            func.count(UserBet.id).label('count'),
        )
        .where(and_(settled_filter, UserBet.settled_at.isnot(None)))
        .group_by(func.date(UserBet.settled_at))
        .order_by(func.date(UserBet.settled_at))
    )
    
    cumulative_pl = 0.0
    daily_pl = []
    for row in daily_result.all():
        date, pl, count = row
        cumulative_pl += pl or 0
        daily_pl.append({
            "date": date.isoformat() if date else None,
            "daily_pl": round(pl or 0, 2),
            "cumulative_pl": round(cumulative_pl, 2),
            "bet_count": count,
        })
    
    return SessionReportResponse(
        date_from=date_from,
        date_to=date_to,
        total_days=total_days,
        total_bets=total_bets,
        settled_bets=settled_bets,
        pending_bets=pending_bets,
        overall_roi=round(overall_roi, 2),
        overall_win_rate=round(overall_win_rate, 4),
        total_profit_loss=round(total_profit_loss, 2),
        total_staked=round(total_staked, 2),
        total_clv=round(total_clv, 2),
        avg_clv=round(avg_clv, 2),
        positive_clv_pct=round(positive_clv_pct, 2),
        by_market=by_market,
        by_sportsbook=by_sportsbook,
        by_sport=by_sport,
        daily_pl=daily_pl,
    )


# Need to import Market for create_bet_from_pick
from app.models import Market
