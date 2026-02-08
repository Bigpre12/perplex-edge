"""
Players API - Simple implementation
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models import Player

router = APIRouter(prefix = " / api / players", tags = ["players"])

@router.get(" / ")
async def get_players(limit: int = Query(default = 50, le = 100),
 db: AsyncSession = Depends(get_db)):
 """Get players list."""
 try:
 result = await db.execute(select(Player).limit(limit))
 players = result.scalars().all()

 return {
 "items": [
 {
 "id": player.id,
 "name": player.name,
 "position": player.position,
 "team_id": player.team_id
 }
 for player in players
 ]
 }
 except Exception as e:
 raise HTTPException(status_code = 500, detail = str(e))

@router.get(" / {player_id}")
async def get_player(player_id: int, db: AsyncSession = Depends(get_db)):
 """Get specific player."""
 try:
 result = await db.execute(select(Player).where(Player.id =  = player_id))
 player = result.scalar_one_or_none()

 if not player:
 raise HTTPException(status_code = 404, detail = "Player not found")

 return {
 "id": player.id,
 "name": player.name,
 "position": player.position,
 "team_id": player.team_id
 }
 except HTTPException:
 raise
 except Exception as e:
 raise HTTPException(status_code = 500, detail = str(e))
