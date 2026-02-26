from fastapi import APIRouter, Depends, Body, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_async_db
from routers.auth_router import get_current_user
from models.users import User
from models.contests import Contest, ContestEntry
from services.contest_service import contest_service
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timezone

router = APIRouter(prefix='/api/contests', tags=['contests'])

class ContestEntryCreate(BaseModel):
    user_id: str
    display_name: str
    contest_id: int
    prop_ids: List[str]

@router.get('/active')
async def get_active_contests(db: AsyncSession = Depends(get_async_db)):
    contests = await contest_service.get_active_contests(db)
    return [{
        'id': c.id, 'name': c.title, 'ends_at': c.end_date.isoformat(),
        'prize_pool': c.prize_pool, 'status': c.status
    } for c in contests]

@router.post('/enter')
async def enter_contest(
    contest_id: int = Body(..., embed=True),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    success, message = await contest_service.join_contest(db, current_user.id, contest_id)
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {'status': 'success', 'message': message}

@router.get('/global-leaderboard')
async def get_global_leaderboard(db: AsyncSession = Depends(get_async_db)):
    leaderboard = await contest_service.get_leaderboard(db)
    return {"status": "success", "leaderboard": leaderboard}

@router.get('/leaderboard/{contest_id}')
async def contest_leaderboard(contest_id: int, db: AsyncSession = Depends(get_async_db)):
    # Simple placeholder for contest-specific leaderboard
    leaderboard = await contest_service.get_leaderboard(db)
    return {"status": "success", "leaderboard": leaderboard}
