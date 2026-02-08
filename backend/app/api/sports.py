"""
Sports API endpoints.

Provides endpoints for listing sports and sport information.
"""

import logging
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from app.core.database import get_db
from app.models import Sport
from app.schemas.sport import SportList, SportResponse

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("", response_model = SportList)
async def list_sports(active_only: bool = Query(True, description = "Filter to active sports only"),
 db: AsyncSession = Depends(get_db),):
 """List all sports."""
 try:
 query = select(Sport)
 if active_only:
 query = query.where(Sport.active =  = True)
 query = query.order_by(Sport.league_code)

 result = await db.execute(query)
 sports = result.scalars().all()

 return SportList(items = [SportResponse.model_validate(s) for s in sports])

 except Exception as e:
 logger.error(f"Error listing sports: {e}")
 raise HTTPException(status_code = 500, detail = f"Failed to list sports: {str(e)}")

@router.get(" / {sport_id}", response_model = SportResponse)
async def get_sport(sport_id: int,
 db: AsyncSession = Depends(get_db),):
 """Get sport by ID."""
 try:
 result = await db.execute(select(Sport).where(Sport.id =  = sport_id))
 sport = result.scalar_one_or_none()

 if not sport:
 raise HTTPException(status_code = 404, detail = "Sport not found")

 return SportResponse.model_validate(sport)

 except HTTPException:
 raise
 except Exception as e:
 logger.error(f"Error getting sport {sport_id}: {e}")
 raise HTTPException(status_code = 500, detail = f"Failed to get sport: {str(e)}")

@router.get(" / league / {league_code}", response_model = SportResponse)
async def get_sport_by_league(league_code: str,
 db: AsyncSession = Depends(get_db),):
 """Get sport by league code."""
 try:
 result = await db.execute(select(Sport).where(Sport.league_code.ilike(f"%{league_code}%")))
 sport = result.scalar_one_or_none()

 if not sport:
 raise HTTPException(status_code = 404, detail = "Sport not found")

 return SportResponse.model_validate(sport)

 except HTTPException:
 raise
 except Exception as e:
 logger.error(f"Error getting sport by league {league_code}: {e}")
 raise HTTPException(status_code = 500, detail = f"Failed to get sport: {str(e)}")
