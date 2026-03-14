class AsyncSession: pass
# apps/api/src/routers/contest_router.py
# Weekly tipster competitions with automated settlement
from fastapi import APIRouter, Depends, Body, Query, HTTPException
from database import get_async_db
from services.contest_service import contest_service
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

router = APIRouter(prefix='/api/contests', tags=['contests'])

class ContestEntryCreate(BaseModel):
    user_id: int
    display_name: str
    contest_id: int
    prop_ids: List[str]

@router.get('/active')
async def get_active_contests(db: AsyncSession = Depends(get_async_db)):
    contests = await contest_service.get_active_contests(db)
    return [{
        'id': c.id, 
        'name': c.title, 
        'description': c.description,
        'prize': c.prize_description, 
        'leg_count': c.required_legs,
        'entries': c.entry_count, 
        'ends_at': c.end_date.isoformat() if c.end_date else None
    } for c in contests]

@router.post('/enter')
async def enter_contest(payload: ContestEntryCreate = Body(...), db: AsyncSession = Depends(get_async_db)):
    success, message = await contest_service.join_contest(
        db, 
        user_id=payload.user_id,
        display_name=payload.display_name,
        contest_id=payload.contest_id,
        prop_ids=payload.prop_ids
    )
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {'status': 'entered', 'message': message}

@router.get('/leaderboard/{contest_id}')
async def contest_leaderboard(contest_id: int, db: AsyncSession = Depends(get_async_db)):
    return await contest_service.get_contest_leaderboard(db, contest_id)

@router.get('/global-leaderboard')
async def global_leaderboard(limit: int = Query(10), db: AsyncSession = Depends(get_async_db)):
    return await contest_service.get_global_leaderboard(db, limit)
