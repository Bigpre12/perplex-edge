"""Games API endpoints."""

from datetime import datetime, timezone, timedelta
from typing import Optional
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models import Game, Sport, Team
from app.schemas.game import GameList, GameWithTeams, GameWithOdds

router = APIRouter()

# Eastern timezone(handles DST automatically)
EASTERN_TZ = ZoneInfo("America / New_York")

@router.get("", response_model = GameList)
async def list_games(sport: Optional[str] = Query(None, description = "Filter by sport(NBA, NFL, etc.)"),
 status: Optional[str] = Query(None, description = "Filter by status"),
 date_from: Optional[datetime] = Query(None, description = "Start date filter"),
 date_to: Optional[datetime] = Query(None, description = "End date filter"),
 limit: int = Query(50, le = 100),
 offset: int = Query(0),
 db: AsyncSession = Depends(get_db),):
 """List games with optional filters."""
 query = (select(Game)
 .options(selectinload(Game.home_team), selectinload(Game.away_team))
 .order_by(Game.start_time))

 # Apply filters
 if sport:
 query = query.join(Sport).where(Sport.league_code.ilike(f"%{sport}%"))

 if status:
 query = query.where(Game.status =  = status)

 if date_from:
 query = query.where(Game.start_time > = date_from)

 if date_to:
 query = query.where(Game.start_time < = date_to)

 # Get total count
 count_query = select(func.count()).select_from(query.subquery())
 total = await db.scalar(count_query)

 # Get paginated results
 query = query.limit(limit).offset(offset)
 result = await db.execute(query)
 games = result.scalars().all()

 return GameList(items = [GameWithTeams.model_validate(g) for g in games],
 total = total or 0,)

@router.get(" / today", response_model = GameList)
async def list_todays_games(sport: Optional[str] = Query(None),
 db: AsyncSession = Depends(get_db),):
 """List today's games(using Eastern time for US sports schedule)."""
 # Use Eastern time to determine "today" (handles DST automatically)
 now_et = datetime.now(EASTERN_TZ)
 today_start_et = now_et.replace(hour = 0, minute = 0, second = 0, microsecond = 0)
 tomorrow_start_et = today_start_et + timedelta(days = 1)

 # Convert to UTC(naive datetimes for PostgreSQL)
 today = today_start_et.astimezone(timezone.utc).replace(tzinfo = None)
 tomorrow = tomorrow_start_et.astimezone(timezone.utc).replace(tzinfo = None)

 query = (select(Game)
 .options(selectinload(Game.home_team), selectinload(Game.away_team))
 .where(Game.start_time > = today, Game.start_time < tomorrow)
 .order_by(Game.start_time))

 if sport:
 query = query.join(Sport).where(Sport.league_code.ilike(f"%{sport}%"))

 result = await db.execute(query)
 games = result.scalars().all()

 return GameList(items = [GameWithTeams.model_validate(g) for g in games],
 total = len(games),)

@router.get(" / {game_id}", response_model = GameWithOdds)
async def get_game(game_id: int,
 db: AsyncSession = Depends(get_db),):
 """Get a specific game with current odds."""
 query = (select(Game)
 .options(selectinload(Game.home_team),
 selectinload(Game.away_team),
 selectinload(Game.lines),)
 .where(Game.id =  = game_id))

 result = await db.execute(query)
 game = result.scalar_one_or_none()

 if not game:
 raise HTTPException(status_code = 404, detail = "Game not found")

 # Build response with odds
 game_data = GameWithTeams.model_validate(game).model_dump()

 # Get current lines
 current_lines = [line for line in game.lines if line.is_current]
 game_data["odds"] = [
 {
 "sportsbook": line.sportsbook,
 "market_type": line.market.market_type if line.market else "unknown",
 "side": line.side,
 "line_value": line.line_value,
 "odds": line.odds,
 }
 for line in current_lines
 ]

 return game_data
