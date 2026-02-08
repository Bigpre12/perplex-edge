"""
Teams API - Simple implementation
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models import Team

router = APIRouter(prefix="/api/teams", tags=["teams"])


@router.get("/")
async def get_teams(
    limit: int = Query(default=50, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Get teams list."""
    try:
        result = await db.execute(select(Team).limit(limit))
        teams = result.scalars().all()
        
        return {
            "items": [
                {
                    "id": team.id,
                    "name": team.name,
                    "abbreviation": team.abbreviation,
                    "sport_id": team.sport_id
                }
                for team in teams
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{team_id}")
async def get_team(team_id: int, db: AsyncSession = Depends(get_db)):
    """Get specific team."""
    try:
        result = await db.execute(select(Team).where(Team.id == team_id))
        team = result.scalar_one_or_none()
        
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")
        
        return {
            "id": team.id,
            "name": team.name,
            "abbreviation": team.abbreviation,
            "sport_id": team.sport_id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
