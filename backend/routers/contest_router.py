# backend/routers/contest_router.py
# Weekly tipster competitions with automated settlement
from fastapi import APIRouter, Depends, Body, Query
from sqlalchemy.orm import Session
from database import get_db
from models import Contest, ContestEntry, BetLog
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import json

router = APIRouter(prefix='/api/contests', tags=['contests'])

class ContestEntryCreate(BaseModel):
    user_id: str
    display_name: str
    contest_id: int
    prop_ids: List[str]

@router.get('/active')
def get_active_contests(db: Session = Depends(get_db)):
    now = datetime.utcnow()
    contests = db.query(Contest).filter(Contest.end_date >= now, Contest.is_active == True).all()
    return [{
        'id': c.id, 'name': c.name, 'sport': c.sport,
        'prize': c.prize_description, 'leg_count': c.required_legs,
        'entries': c.entry_count, 'ends_at': c.end_date.isoformat()
    } for c in contests]

@router.post('/enter')
def enter_contest(payload: ContestEntryCreate = Body(...), db: Session = Depends(get_db)):
    contest = db.query(Contest).filter(Contest.id == payload.contest_id).first()
    if not contest or not contest.is_active:
        return {'error': 'Contest not found or closed'}
    if len(payload.prop_ids) != contest.required_legs:
        return {'error': f'Must submit exactly {contest.required_legs} legs'}
    existing = db.query(ContestEntry).filter(
        ContestEntry.user_id == payload.user_id,
        ContestEntry.contest_id == payload.contest_id
    ).first()
    if existing:
        return {'error': 'Already entered this contest'}
    entry = ContestEntry(user_id=payload.user_id, display_name=payload.display_name,
                          contest_id=payload.contest_id, prop_ids_json=json.dumps(payload.prop_ids),
                          hits=0, total_legs=len(payload.prop_ids),
                          submitted_at=datetime.utcnow())
    db.add(entry)
    contest.entry_count = (contest.entry_count or 0) + 1
    db.commit()
    return {'status': 'entered', 'contest': contest.name, 'legs': len(payload.prop_ids)}

@router.get('/leaderboard/{contest_id}')
def contest_leaderboard(contest_id: int, db: Session = Depends(get_db)):
    entries = db.query(ContestEntry).filter(ContestEntry.contest_id == contest_id).order_by(ContestEntry.hits.desc()).limit(20).all()
    return [{'rank': i+1, 'user': e.display_name, 'hits': e.hits, 'total': e.total_legs,
             'hit_rate': round(e.hits / e.total_legs * 100, 1) if e.total_legs else 0} for i, e in enumerate(entries)]
