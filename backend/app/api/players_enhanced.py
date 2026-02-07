"""
Enhanced Players API - Advanced filtering, search, and relationships
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models import Player, Team, Sport, ModelPick

router = APIRouter(prefix="/api/players", tags=["players"])


@router.get("/")
async def get_players(
    sport_id: int = Query(None, description="Filter by sport ID"),
    team_id: int = Query(None, description="Filter by team ID"),
    search: str = Query(None, description="Search by name or position"),
    position: str = Query(None, description="Filter by position"),
    limit: int = Query(default=50, le=1000),
    offset: int = Query(default=0),
    db: AsyncSession = Depends(get_db)
):
    """Get players with advanced filtering and search."""
    try:
        # Build base query with relationships
        query = select(Player).options(
            selectinload(Player.team).selectinload(Team.sport),
            selectinload(Player.model_picks)
        )
        
        # Apply filters
        conditions = []
        
        if sport_id:
            conditions.append(Player.team.has(Team.sport_id == sport_id))
        
        if team_id:
            conditions.append(Player.team_id == team_id)
        
        if position:
            conditions.append(Player.position.ilike(f"%{position}%"))
        
        if search:
            search_conditions = [
                Player.name.ilike(f"%{search}%"),
                Player.position.ilike(f"%{search}%")
            ]
            conditions.append(or_(*search_conditions))
        
        if conditions:
            query = query.where(and_(*conditions))
        
        # Apply pagination
        query = query.offset(offset).limit(limit)
        
        result = await db.execute(query)
        players = result.scalars().all()
        
        # Format response
        items = []
        for player in players:
            player_data = {
                "id": player.id,
                "name": player.name,
                "position": player.position,
                "jersey_number": player.jersey_number,
                "height": player.height,
                "weight": player.weight,
                "birth_date": player.birth_date.isoformat() if player.birth_date else None,
                "college": player.college,
                "draft_year": player.draft_year,
                "draft_round": player.draft_round,
                "draft_pick": player.draft_pick,
                "team_id": player.team_id,
                "team_name": player.team.name if player.team else None,
                "team_abbreviation": player.team.abbreviation if player.team else None,
                "sport_id": player.team.sport.id if player.team and player.team.sport else None,
                "sport_name": player.team.sport.name if player.team and player.team.sport else None,
                "created_at": player.created_at.isoformat() if player.created_at else None,
                "updated_at": player.updated_at.isoformat() if player.updated_at else None
            }
            items.append(player_data)
        
        return {
            "items": items,
            "total": len(items),
            "limit": limit,
            "offset": offset,
            "filters": {
                "sport_id": sport_id,
                "team_id": team_id,
                "search": search,
                "position": position
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{player_id}")
async def get_player(player_id: int, db: AsyncSession = Depends(get_db)):
    """Get specific player with full details."""
    try:
        result = await db.execute(
            select(Player)
            .options(
                selectinload(Player.team).selectinload(Team.sport),
                selectinload(Player.model_picks)
            )
            .where(Player.id == player_id)
        )
        player = result.scalar_one_or_none()
        
        if not player:
            raise HTTPException(status_code=404, detail="Player not found")
        
        # Get player statistics if available
        stats = []
        try:
            from app.models import PlayerStat
            stats_result = await db.execute(
                select(PlayerStat).where(PlayerStat.player_id == player_id)
                .order_by(PlayerStat.season.desc())
                .limit(5)
            )
            stats = stats_result.scalars().all()
        except ImportError:
            # PlayerStat model not available
            pass
        
        player_data = {
            "id": player.id,
            "name": player.name,
            "position": player.position,
            "jersey_number": player.jersey_number,
            "height": player.height,
            "weight": player.weight,
            "birth_date": player.birth_date.isoformat() if player.birth_date else None,
            "college": player.college,
            "draft_year": player.draft_year,
            "draft_round": player.draft_round,
            "draft_pick": player.draft_pick,
            "team_id": player.team_id,
            "team_name": player.team.name if player.team else None,
            "team_abbreviation": player.team.abbreviation if player.team else None,
            "sport_id": player.team.sport.id if player.team and player.team.sport else None,
            "sport_name": player.team.sport.name if player.team and player.team.sport else None,
            "created_at": player.created_at.isoformat() if player.created_at else None,
            "updated_at": player.updated_at.isoformat() if player.updated_at else None,
            "statistics": [
                {
                    "season": stat.season,
                    "games_played": stat.games_played,
                    "points_per_game": stat.points_per_game,
                    "rebounds_per_game": stat.rebounds_per_game,
                    "assists_per_game": stat.assists_per_game,
                    "field_goal_percentage": stat.field_goal_percentage
                }
                for stat in stats
            ] if stats else []
        }
        
        return player_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search/{search_term}")
async def search_players(
    search_term: str,
    sport_id: int = Query(None, description="Filter by sport"),
    position: str = Query(None, description="Filter by position"),
    limit: int = Query(default=20, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Search players by name or position."""
    try:
        query = select(Player).options(
            selectinload(Player.team).selectinload(Team.sport)
        )
        
        # Build search conditions
        search_conditions = [
            Player.name.ilike(f"%{search_term}%"),
            Player.position.ilike(f"%{search_term}%")
        ]
        
        conditions = [or_(*search_conditions)]
        
        if sport_id:
            conditions.append(Player.team.has(Team.sport_id == sport_id))
        
        if position:
            conditions.append(Player.position.ilike(f"%{position}%"))
        
        query = query.where(and_(*conditions)).limit(limit)
        
        result = await db.execute(query)
        players = result.scalars().all()
        
        items = []
        for player in players:
            player_data = {
                "id": player.id,
                "name": player.name,
                "position": player.position,
                "team_name": player.team.name if player.team else None,
                "team_abbreviation": player.team.abbreviation if player.team else None,
                "sport_name": player.team.sport.name if player.team and player.team.sport else None
            }
            items.append(player_data)
        
        return {
            "search_term": search_term,
            "items": items,
            "total": len(items),
            "filters": {
                "sport_id": sport_id,
                "position": position
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/team/{team_id}")
async def get_team_players(
    team_id: int,
    position: str = Query(None, description="Filter by position"),
    limit: int = Query(default=50, le=1000),
    offset: int = Query(default=0),
    db: AsyncSession = Depends(get_db)
):
    """Get all players for a specific team."""
    try:
        query = select(Player).options(
            selectinload(Player.team).selectinload(Team.sport)
        ).where(Player.team_id == team_id)
        
        if position:
            query = query.where(Player.position.ilike(f"%{position}%"))
        
        query = query.offset(offset).limit(limit)
        
        result = await db.execute(query)
        players = result.scalars().all()
        
        items = []
        for player in players:
            player_data = {
                "id": player.id,
                "name": player.name,
                "position": player.position,
                "jersey_number": player.jersey_number,
                "height": player.height,
                "weight": player.weight,
                "college": player.college,
                "draft_year": player.draft_year
            }
            items.append(player_data)
        
        return {
            "team_id": team_id,
            "items": items,
            "total": len(items),
            "limit": limit,
            "offset": offset,
            "filters": {
                "position": position
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sport/{sport_id}")
async def get_sport_players(
    sport_id: int,
    position: str = Query(None, description="Filter by position"),
    search: str = Query(None, description="Search by name"),
    limit: int = Query(default=100, le=1000),
    offset: int = Query(default=0),
    db: AsyncSession = Depends(get_db)
):
    """Get all players for a specific sport."""
    try:
        query = select(Player).options(
            selectinload(Player.team).selectinload(Team.sport)
        ).where(Player.team.has(Team.sport_id == sport_id))
        
        conditions = []
        
        if position:
            conditions.append(Player.position.ilike(f"%{position}%"))
        
        if search:
            conditions.append(Player.name.ilike(f"%{search}%"))
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.offset(offset).limit(limit)
        
        result = await db.execute(query)
        players = result.scalars().all()
        
        items = []
        for player in players:
            player_data = {
                "id": player.id,
                "name": player.name,
                "position": player.position,
                "team_name": player.team.name if player.team else None,
                "team_abbreviation": player.team.abbreviation if player.team else None,
                "jersey_number": player.jersey_number,
                "height": player.height,
                "weight": player.weight
            }
            items.append(player_data)
        
        return {
            "sport_id": sport_id,
            "items": items,
            "total": len(items),
            "limit": limit,
            "offset": offset,
            "filters": {
                "position": position,
                "search": search
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
