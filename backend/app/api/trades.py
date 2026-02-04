"""Trades API routes for tracking NBA trades."""

import logging
from datetime import date
from typing import Optional, List

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models import Trade, TradeDetail, Player, Team, Season, SeasonRoster
from app.schemas.trade import (
    TradeCreate, TradeRead, TradeList, TradeWithDetails,
    TradeDetailWithTeams,
    TradeApplyRequest, TradeApplyResult,
    BulkTradeCreate, BulkTradeResult,
)


logger = logging.getLogger(__name__)
router = APIRouter()


# =============================================================================
# Helper Functions
# =============================================================================

async def get_team_by_name(db: AsyncSession, team_name: str, sport_id: int = 30) -> Optional[Team]:
    """Find a team by name or abbreviation."""
    # Normalize the team name
    team_name_lower = team_name.lower().strip()
    
    # Try exact match first
    result = await db.execute(
        select(Team).where(
            and_(
                Team.sport_id == sport_id,
                or_(
                    Team.name.ilike(f"%{team_name}%"),
                    Team.abbreviation.ilike(team_name),
                )
            )
        )
    )
    team = result.scalar_one_or_none()
    
    if team:
        return team
    
    # Try common name mappings
    name_mappings = {
        "cavaliers": "Cleveland Cavaliers",
        "cavs": "Cleveland Cavaliers",
        "clippers": "Los Angeles Clippers",
        "lac": "Los Angeles Clippers",
        "celtics": "Boston Celtics",
        "bulls": "Chicago Bulls",
        "jazz": "Utah Jazz",
        "grizzlies": "Memphis Grizzlies",
        "wizards": "Washington Wizards",
        "hawks": "Atlanta Hawks",
        "rockets": "Houston Rockets",
        "suns": "Phoenix Suns",
        "nets": "Brooklyn Nets",
        "blazers": "Portland Trail Blazers",
        "trail blazers": "Portland Trail Blazers",
        "pistons": "Detroit Pistons",
        "timberwolves": "Minnesota Timberwolves",
        "wolves": "Minnesota Timberwolves",
        "kings": "Sacramento Kings",
        "lakers": "Los Angeles Lakers",
        "knicks": "New York Knicks",
        "heat": "Miami Heat",
        "bucks": "Milwaukee Bucks",
        "nuggets": "Denver Nuggets",
        "warriors": "Golden State Warriors",
        "spurs": "San Antonio Spurs",
        "raptors": "Toronto Raptors",
        "pacers": "Indiana Pacers",
        "magic": "Orlando Magic",
        "hornets": "Charlotte Hornets",
        "pelicans": "New Orleans Pelicans",
        "mavericks": "Dallas Mavericks",
        "mavs": "Dallas Mavericks",
        "thunder": "Oklahoma City Thunder",
        "okc": "Oklahoma City Thunder",
    }
    
    mapped_name = name_mappings.get(team_name_lower)
    if mapped_name:
        result = await db.execute(
            select(Team).where(
                and_(
                    Team.sport_id == sport_id,
                    Team.name == mapped_name,
                )
            )
        )
        return result.scalar_one_or_none()
    
    return None


async def get_player_by_name(db: AsyncSession, player_name: str, sport_id: int = 30) -> Optional[Player]:
    """Find a player by name."""
    result = await db.execute(
        select(Player).where(
            and_(
                Player.sport_id == sport_id,
                Player.name.ilike(f"%{player_name}%"),
            )
        )
    )
    return result.scalar_one_or_none()


def build_trade_response(trade: Trade) -> TradeWithDetails:
    """Build a TradeWithDetails response from a Trade model."""
    teams_involved = set()
    players_moved = []
    
    details_with_teams = []
    for detail in trade.details:
        teams_involved.add(detail.from_team.name if detail.from_team else str(detail.from_team_id))
        teams_involved.add(detail.to_team.name if detail.to_team else str(detail.to_team_id))
        
        if detail.asset_type == "player" and detail.player_name:
            players_moved.append(detail.player_name)
        
        details_with_teams.append(TradeDetailWithTeams(
            id=detail.id,
            trade_id=detail.trade_id,
            player_id=detail.player_id,
            from_team_id=detail.from_team_id,
            to_team_id=detail.to_team_id,
            asset_type=detail.asset_type,
            asset_description=detail.asset_description,
            player_name=detail.player_name,
            created_at=detail.created_at,
            from_team_name=detail.from_team.name if detail.from_team else None,
            from_team_abbr=detail.from_team.abbreviation if detail.from_team else None,
            to_team_name=detail.to_team.name if detail.to_team else None,
            to_team_abbr=detail.to_team.abbreviation if detail.to_team else None,
        ))
    
    return TradeWithDetails(
        id=trade.id,
        trade_date=trade.trade_date,
        season_year=trade.season_year,
        description=trade.description,
        headline=trade.headline,
        source_url=trade.source_url,
        source=trade.source,
        is_applied=trade.is_applied,
        created_at=trade.created_at,
        updated_at=trade.updated_at,
        details=details_with_teams,
        teams_involved=list(teams_involved),
        players_moved=players_moved,
    )


# =============================================================================
# Trade List & Detail Endpoints
# =============================================================================

@router.get("/trades", response_model=TradeList, tags=["trades"])
async def list_trades(
    season_year: Optional[int] = Query(None, description="Filter by season year (e.g., 2026)"),
    team: Optional[str] = Query(None, description="Filter by team name"),
    player: Optional[str] = Query(None, description="Filter by player name"),
    applied_only: bool = Query(False, description="Only show applied trades"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """
    List all trades with optional filters.
    
    Filters:
    - season_year: Filter by NBA season (e.g., 2026 for 2025-26)
    - team: Filter by team involved in trade
    - player: Filter by player traded
    - applied_only: Only show trades that have been applied
    """
    query = (
        select(Trade)
        .options(
            selectinload(Trade.details).selectinload(TradeDetail.from_team),
            selectinload(Trade.details).selectinload(TradeDetail.to_team),
            selectinload(Trade.details).selectinload(TradeDetail.player),
        )
        .order_by(Trade.trade_date.desc(), Trade.created_at.desc())
    )
    
    if season_year:
        query = query.where(Trade.season_year == season_year)
    
    if applied_only:
        query = query.where(Trade.is_applied == True)
    
    if team:
        # Find team ID
        team_obj = await get_team_by_name(db, team)
        if team_obj:
            query = query.join(Trade.details).where(
                or_(
                    TradeDetail.from_team_id == team_obj.id,
                    TradeDetail.to_team_id == team_obj.id,
                )
            ).distinct()
    
    if player:
        query = query.join(Trade.details).where(
            TradeDetail.player_name.ilike(f"%{player}%")
        ).distinct()
    
    # Get total count
    from sqlalchemy import func
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query) or 0
    
    # Apply pagination
    query = query.limit(limit).offset(offset)
    
    result = await db.execute(query)
    trades = result.scalars().unique().all()
    
    return TradeList(
        items=[build_trade_response(t) for t in trades],
        total=total,
    )


@router.get("/trades/{trade_id}", response_model=TradeWithDetails, tags=["trades"])
async def get_trade(
    trade_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific trade by ID with all details."""
    result = await db.execute(
        select(Trade)
        .options(
            selectinload(Trade.details).selectinload(TradeDetail.from_team),
            selectinload(Trade.details).selectinload(TradeDetail.to_team),
            selectinload(Trade.details).selectinload(TradeDetail.player),
        )
        .where(Trade.id == trade_id)
    )
    trade = result.scalar_one_or_none()
    
    if not trade:
        raise HTTPException(status_code=404, detail="Trade not found")
    
    return build_trade_response(trade)


@router.get("/trades/player/{player_id}", response_model=TradeList, tags=["trades"])
async def get_player_trade_history(
    player_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get trade history for a specific player."""
    # Get player
    player = await db.get(Player, player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    # Find trades involving this player
    result = await db.execute(
        select(Trade)
        .options(
            selectinload(Trade.details).selectinload(TradeDetail.from_team),
            selectinload(Trade.details).selectinload(TradeDetail.to_team),
            selectinload(Trade.details).selectinload(TradeDetail.player),
        )
        .join(Trade.details)
        .where(
            or_(
                TradeDetail.player_id == player_id,
                TradeDetail.player_name.ilike(f"%{player.name}%"),
            )
        )
        .order_by(Trade.trade_date.desc())
        .distinct()
    )
    trades = result.scalars().unique().all()
    
    return TradeList(
        items=[build_trade_response(t) for t in trades],
        total=len(trades),
    )


# =============================================================================
# Trade Create Endpoints
# =============================================================================

@router.post("/trades", response_model=TradeWithDetails, tags=["trades"])
async def create_trade(
    trade_data: TradeCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new trade record.
    
    This creates the trade in the database but does NOT automatically
    update player team assignments. Call `/trades/apply/{trade_id}` to apply.
    """
    # Create the trade
    trade = Trade(
        trade_date=trade_data.trade_date,
        season_year=trade_data.season_year,
        description=trade_data.description,
        headline=trade_data.headline,
        source_url=trade_data.source_url,
        source=trade_data.source,
        is_applied=False,
    )
    db.add(trade)
    await db.flush()
    
    # Create trade details
    for detail_data in trade_data.details:
        # Try to find player if player_id not provided but name is
        player_id = detail_data.player_id
        if not player_id and detail_data.player_name:
            player = await get_player_by_name(db, detail_data.player_name)
            if player:
                player_id = player.id
        
        detail = TradeDetail(
            trade_id=trade.id,
            player_id=player_id,
            from_team_id=detail_data.from_team_id,
            to_team_id=detail_data.to_team_id,
            asset_type=detail_data.asset_type,
            asset_description=detail_data.asset_description,
            player_name=detail_data.player_name,
        )
        db.add(detail)
    
    await db.commit()
    
    # Reload with relationships
    result = await db.execute(
        select(Trade)
        .options(
            selectinload(Trade.details).selectinload(TradeDetail.from_team),
            selectinload(Trade.details).selectinload(TradeDetail.to_team),
            selectinload(Trade.details).selectinload(TradeDetail.player),
        )
        .where(Trade.id == trade.id)
    )
    trade = result.scalar_one()
    
    logger.info(f"Created trade {trade.id}: {trade.headline}")
    return build_trade_response(trade)


@router.post("/trades/bulk", response_model=BulkTradeResult, tags=["trades"])
async def bulk_create_trades(
    bulk_data: BulkTradeCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Bulk create multiple trades from simplified format.
    
    Example input:
    ```json
    {
        "season_year": 2026,
        "trades": [
            {
                "trade_date": "2026-02-03",
                "headline": "Harden to Cavaliers",
                "players": [
                    {"name": "James Harden", "from": "Clippers", "to": "Cavaliers"},
                    {"name": "Darius Garland", "from": "Cavaliers", "to": "Clippers"}
                ],
                "picks": [
                    {"description": "2027 1st round pick", "from": "Cavaliers", "to": "Clippers"}
                ]
            }
        ],
        "auto_apply": true
    }
    ```
    """
    trades_created = 0
    details_created = 0
    players_updated = 0
    errors = []
    
    for trade_item in bulk_data.trades:
        try:
            # Create trade
            trade = Trade(
                trade_date=trade_item.trade_date,
                season_year=bulk_data.season_year,
                headline=trade_item.headline,
                description=trade_item.description,
                source_url=trade_item.source_url,
                source="nba.com",
                is_applied=False,
            )
            db.add(trade)
            await db.flush()
            trades_created += 1
            
            # Add player details
            for player_info in trade_item.players:
                from_team = await get_team_by_name(db, player_info.get("from", ""))
                to_team = await get_team_by_name(db, player_info.get("to", ""))
                
                if not from_team or not to_team:
                    errors.append(f"Could not find teams for {player_info['name']}")
                    continue
                
                player = await get_player_by_name(db, player_info["name"])
                
                detail = TradeDetail(
                    trade_id=trade.id,
                    player_id=player.id if player else None,
                    from_team_id=from_team.id,
                    to_team_id=to_team.id,
                    asset_type="player",
                    player_name=player_info["name"],
                )
                db.add(detail)
                details_created += 1
            
            # Add pick details
            if trade_item.picks:
                for pick_info in trade_item.picks:
                    from_team = await get_team_by_name(db, pick_info.get("from", ""))
                    to_team = await get_team_by_name(db, pick_info.get("to", ""))
                    
                    if from_team and to_team:
                        detail = TradeDetail(
                            trade_id=trade.id,
                            from_team_id=from_team.id,
                            to_team_id=to_team.id,
                            asset_type="pick",
                            asset_description=pick_info.get("description", "Draft pick"),
                        )
                        db.add(detail)
                        details_created += 1
            
            # Auto-apply if requested
            if bulk_data.auto_apply:
                apply_result = await _apply_trade_internal(db, trade)
                players_updated += apply_result["players_updated"]
                trade.is_applied = True
            
        except Exception as e:
            errors.append(f"Error creating trade {trade_item.headline}: {str(e)}")
            logger.error(f"Bulk trade error: {e}")
    
    await db.commit()
    
    return BulkTradeResult(
        trades_created=trades_created,
        details_created=details_created,
        players_updated=players_updated,
        errors=errors,
    )


# =============================================================================
# Trade Apply Endpoint
# =============================================================================

async def _apply_trade_internal(db: AsyncSession, trade: Trade) -> dict:
    """Internal function to apply a trade."""
    players_updated = 0
    roster_created = 0
    roster_deactivated = 0
    details = []
    
    for detail in trade.details:
        if detail.asset_type != "player":
            continue
        
        # Find player
        player = None
        if detail.player_id:
            player = await db.get(Player, detail.player_id)
        elif detail.player_name:
            player = await get_player_by_name(db, detail.player_name)
        
        if not player:
            details.append({
                "player_name": detail.player_name,
                "status": "not_found",
            })
            continue
        
        old_team_id = player.team_id
        
        # Update player's team
        player.team_id = detail.to_team_id
        players_updated += 1
        
        # Update SeasonRoster if season exists
        season_result = await db.execute(
            select(Season).where(
                and_(
                    Season.sport_id == player.sport_id,
                    Season.season_year == trade.season_year,
                )
            )
        )
        season = season_result.scalar_one_or_none()
        
        if season:
            # Deactivate old roster entry
            if old_team_id:
                old_roster_result = await db.execute(
                    select(SeasonRoster).where(
                        and_(
                            SeasonRoster.season_id == season.id,
                            SeasonRoster.player_id == player.id,
                            SeasonRoster.team_id == old_team_id,
                            SeasonRoster.is_active == True,
                        )
                    )
                )
                old_roster = old_roster_result.scalar_one_or_none()
                if old_roster:
                    old_roster.is_active = False
                    roster_deactivated += 1
            
            # Create new roster entry
            new_roster = SeasonRoster(
                season_id=season.id,
                team_id=detail.to_team_id,
                player_id=player.id,
                is_active=True,
            )
            db.add(new_roster)
            roster_created += 1
        
        details.append({
            "player_name": player.name,
            "player_id": player.id,
            "old_team_id": old_team_id,
            "new_team_id": detail.to_team_id,
            "status": "updated",
        })
    
    return {
        "players_updated": players_updated,
        "roster_entries_created": roster_created,
        "roster_entries_deactivated": roster_deactivated,
        "details": details,
    }


@router.post("/trades/apply/{trade_id}", response_model=TradeApplyResult, tags=["trades"])
async def apply_trade(
    trade_id: int,
    request: TradeApplyRequest = TradeApplyRequest(),
    db: AsyncSession = Depends(get_db),
):
    """
    Apply a trade to update player team assignments.
    
    This will:
    1. Update Player.team_id for each traded player
    2. Optionally update SeasonRoster entries (deactivate old, create new)
    """
    # Get trade with details
    result = await db.execute(
        select(Trade)
        .options(selectinload(Trade.details))
        .where(Trade.id == trade_id)
    )
    trade = result.scalar_one_or_none()
    
    if not trade:
        raise HTTPException(status_code=404, detail="Trade not found")
    
    if trade.is_applied:
        raise HTTPException(status_code=400, detail="Trade has already been applied")
    
    # Apply the trade
    apply_result = await _apply_trade_internal(db, trade)
    
    # Mark trade as applied
    trade.is_applied = True
    
    await db.commit()
    
    logger.info(
        f"Applied trade {trade_id}: {apply_result['players_updated']} players updated"
    )
    
    return TradeApplyResult(
        trade_id=trade_id,
        players_updated=apply_result["players_updated"],
        roster_entries_created=apply_result["roster_entries_created"],
        roster_entries_deactivated=apply_result["roster_entries_deactivated"],
        details=apply_result["details"],
    )
