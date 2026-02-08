"""
Enhanced Teams API - Advanced filtering, search, and roster management
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models import Team, Sport, Player

router = APIRouter(prefix = " / api / teams", tags = ["teams"])

@router.get(" / ")
async def get_teams(sport_id: int = Query(None, description = "Filter by sport ID"),
 search: str = Query(None, description = "Search by name or abbreviation"),
 conference: str = Query(None, description = "Filter by conference"),
 division: str = Query(None, description = "Filter by division"),
 limit: int = Query(default = 50, le = 1000),
 offset: int = Query(default = 0),
 db: AsyncSession = Depends(get_db)):
 """Get teams with advanced filtering and search."""
 try:
 # Build base query with relationships
 query = select(Team).options(selectinload(Team.sport),
 selectinload(Team.players))

 # Apply filters
 conditions = []

 if sport_id:
 conditions.append(Team.sport_id =  = sport_id)

 if search:
 search_conditions = [
 Team.name.ilike(f"%{search}%"),
 Team.abbreviation.ilike(f"%{search}%")
 ]
 conditions.append(or_( * search_conditions))

 if conference:
 conditions.append(Team.conference.ilike(f"%{conference}%"))

 if division:
 conditions.append(Team.division.ilike(f"%{division}%"))

 if conditions:
 query = query.where(and_( * conditions))

 # Apply pagination
 query = query.offset(offset).limit(limit)

 result = await db.execute(query)
 teams = result.scalars().all()

 # Format response
 items = []
 for team in teams:
 team_data = {
 "id": team.id,
 "name": team.name,
 "abbreviation": team.abbreviation,
 "conference": team.conference,
 "division": team.division,
 "founded_year": team.founded_year,
 "arena": team.arena,
 "capacity": team.capacity,
 "owner": team.owner,
 "general_manager": team.general_manager,
 "head_coach": team.head_coach,
 "sport_id": team.sport_id,
 "sport_name": team.sport.name if team.sport else None,
 "logo_url": team.logo_url,
 "primary_color": team.primary_color,
 "secondary_color": team.secondary_color,
 "roster_count": len(team.players) if team.players else 0,
 "created_at": team.created_at.isoformat() if team.created_at else None,
 "updated_at": team.updated_at.isoformat() if team.updated_at else None
 }
 items.append(team_data)

 return {
 "items": items,
 "total": len(items),
 "limit": limit,
 "offset": offset,
 "filters": {
 "sport_id": sport_id,
 "search": search,
 "conference": conference,
 "division": division
 }
 }

 except Exception as e:
 raise HTTPException(status_code = 500, detail = str(e))

@router.get(" / {team_id}")
async def get_team(team_id: int, db: AsyncSession = Depends(get_db)):
 """Get specific team with full details and roster."""
 try:
 result = await db.execute(select(Team)
 .options(selectinload(Team.sport),
 selectinload(Team.players).selectinload(Player.team))
 .where(Team.id =  = team_id))
 team = result.scalar_one_or_none()

 if not team:
 raise HTTPException(status_code = 404, detail = "Team not found")

 # Format roster
 roster = []
 if team.players:
 for player in team.players:
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
 roster.append(player_data)

 team_data = {
 "id": team.id,
 "name": team.name,
 "abbreviation": team.abbreviation,
 "conference": team.conference,
 "division": team.division,
 "founded_year": team.founded_year,
 "arena": team.arena,
 "capacity": team.capacity,
 "owner": team.owner,
 "general_manager": team.general_manager,
 "head_coach": team.head_coach,
 "sport_id": team.sport_id,
 "sport_name": team.sport.name if team.sport else None,
 "logo_url": team.logo_url,
 "primary_color": team.primary_color,
 "secondary_color": team.secondary_color,
 "roster": roster,
 "roster_count": len(roster),
 "created_at": team.created_at.isoformat() if team.created_at else None,
 "updated_at": team.updated_at.isoformat() if team.updated_at else None
 }

 return team_data

 except HTTPException:
 raise
 except Exception as e:
 raise HTTPException(status_code = 500, detail = str(e))

@router.get(" / search / {search_term}")
async def search_teams(search_term: str,
 sport_id: int = Query(None, description = "Filter by sport"),
 conference: str = Query(None, description = "Filter by conference"),
 limit: int = Query(default = 20, le = 100),
 db: AsyncSession = Depends(get_db)):
 """Search teams by name or abbreviation."""
 try:
 query = select(Team).options(selectinload(Team.sport))

 # Build search conditions
 search_conditions = [
 Team.name.ilike(f"%{search_term}%"),
 Team.abbreviation.ilike(f"%{search_term}%")
 ]

 conditions = [or_( * search_conditions)]

 if sport_id:
 conditions.append(Team.sport_id =  = sport_id)

 if conference:
 conditions.append(Team.conference.ilike(f"%{conference}%"))

 query = query.where(and_( * conditions)).limit(limit)

 result = await db.execute(query)
 teams = result.scalars().all()

 items = []
 for team in teams:
 team_data = {
 "id": team.id,
 "name": team.name,
 "abbreviation": team.abbreviation,
 "conference": team.conference,
 "division": team.division,
 "sport_name": team.sport.name if team.sport else None,
 "arena": team.arena,
 "head_coach": team.head_coach
 }
 items.append(team_data)

 return {
 "search_term": search_term,
 "items": items,
 "total": len(items),
 "filters": {
 "sport_id": sport_id,
 "conference": conference
 }
 }

 except Exception as e:
 raise HTTPException(status_code = 500, detail = str(e))

@router.get(" / sport / {sport_id}")
async def get_sport_teams(sport_id: int,
 conference: str = Query(None, description = "Filter by conference"),
 division: str = Query(None, description = "Filter by division"),
 search: str = Query(None, description = "Search by name"),
 limit: int = Query(default = 100, le = 1000),
 offset: int = Query(default = 0),
 db: AsyncSession = Depends(get_db)):
 """Get all teams for a specific sport."""
 try:
 query = select(Team).options(selectinload(Team.sport),
 selectinload(Team.players)).where(Team.sport_id =  = sport_id)

 conditions = []

 if conference:
 conditions.append(Team.conference.ilike(f"%{conference}%"))

 if division:
 conditions.append(Team.division.ilike(f"%{division}%"))

 if search:
 conditions.append(Team.name.ilike(f"%{search}%"))

 if conditions:
 query = query.where(and_( * conditions))

 query = query.offset(offset).limit(limit)

 result = await db.execute(query)
 teams = result.scalars().all()

 items = []
 for team in teams:
 team_data = {
 "id": team.id,
 "name": team.name,
 "abbreviation": team.abbreviation,
 "conference": team.conference,
 "division": team.division,
 "arena": team.arena,
 "capacity": team.capacity,
 "head_coach": team.head_coach,
 "roster_count": len(team.players) if team.players else 0
 }
 items.append(team_data)

 return {
 "sport_id": sport_id,
 "items": items,
 "total": len(items),
 "limit": limit,
 "offset": offset,
 "filters": {
 "conference": conference,
 "division": division,
 "search": search
 }
 }

 except Exception as e:
 raise HTTPException(status_code = 500, detail = str(e))

@router.get(" / conference / {sport_id} / {conference}")
async def get_conference_teams(sport_id: int,
 conference: str,
 division: str = Query(None, description = "Filter by division"),
 limit: int = Query(default = 50, le = 1000),
 offset: int = Query(default = 0),
 db: AsyncSession = Depends(get_db)):
 """Get all teams in a specific conference."""
 try:
 query = select(Team).options(selectinload(Team.sport),
 selectinload(Team.players)).where(and_(Team.sport_id =  = sport_id,
 Team.conference.ilike(f"%{conference}%")))

 if division:
 query = query.where(Team.division.ilike(f"%{division}%"))

 query = query.offset(offset).limit(limit)

 result = await db.execute(query)
 teams = result.scalars().all()

 items = []
 for team in teams:
 team_data = {
 "id": team.id,
 "name": team.name,
 "abbreviation": team.abbreviation,
 "division": team.division,
 "arena": team.arena,
 "capacity": team.capacity,
 "head_coach": team.head_coach,
 "roster_count": len(team.players) if team.players else 0
 }
 items.append(team_data)

 return {
 "sport_id": sport_id,
 "conference": conference,
 "items": items,
 "total": len(items),
 "limit": limit,
 "offset": offset,
 "filters": {
 "division": division
 }
 }

 except Exception as e:
 raise HTTPException(status_code = 500, detail = str(e))

@router.get(" / {team_id} / roster")
async def get_team_roster(team_id: int,
 position: str = Query(None, description = "Filter by position"),
 search: str = Query(None, description = "Search by name"),
 limit: int = Query(default = 50, le = 1000),
 offset: int = Query(default = 0),
 db: AsyncSession = Depends(get_db)):
 """Get team roster with advanced filtering."""
 try:
 # Get team info
 team_result = await db.execute(select(Team).options(selectinload(Team.sport))
 .where(Team.id =  = team_id))
 team = team_result.scalar_one_or_none()

 if not team:
 raise HTTPException(status_code = 404, detail = "Team not found")

 # Get players for this team
 query = select(Player).where(Player.team_id =  = team_id)

 conditions = []

 if position:
 conditions.append(Player.position.ilike(f"%{position}%"))

 if search:
 conditions.append(Player.name.ilike(f"%{search}%"))

 if conditions:
 query = query.where(and_( * conditions))

 query = query.offset(offset).limit(limit)

 result = await db.execute(query)
 players = result.scalars().all()

 # Format roster
 roster = []
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
 "draft_pick": player.draft_pick
 }
 roster.append(player_data)

 return {
 "team_id": team_id,
 "team_name": team.name,
 "team_abbreviation": team.abbreviation,
 "sport_name": team.sport.name if team.sport else None,
 "roster": roster,
 "total": len(roster),
 "limit": limit,
 "offset": offset,
 "filters": {
 "position": position,
 "search": search
 }
 }

 except HTTPException:
 raise
 except Exception as e:
 raise HTTPException(status_code = 500, detail = str(e))
