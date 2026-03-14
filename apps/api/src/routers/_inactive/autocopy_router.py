# backend/routers/autocopy_router.py
from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from database import get_db
from models.props import PropLine
from typing import List

router = APIRouter(prefix='/api/copy', tags=['autocopy'])

@router.post('/prizepicks-slip')
def build_prizepicks_slip(prop_ids: List[str] = Body(...), db: Session = Depends(get_db)):
    props = db.query(PropLine).filter(PropLine.id.in_(prop_ids)).all()
    lines = []
    for p in props:
        lines.append(f"{p.player_name} | {p.stat_category.upper()} {p.line} OVER")
    slip_text = '\n'.join(lines)
    return {
        'slip_text': slip_text,
        'leg_count': len(props),
        'format': 'prizepicks',
        'props': [{'player': p.player_name, 'stat': p.stat_category, 'line': p.line, 'side': 'OVER'} for p in props]
    }

@router.post('/fliff-slip')
def build_fliff_slip(prop_ids: List[str] = Body(...), db: Session = Depends(get_db)):
    props = db.query(PropLine).filter(PropLine.id.in_(prop_ids)).all()
    lines = [f"{p.player_name} {p.stat_category} O{p.line}" for p in props]
    return {'slip_text': '\n'.join(lines), 'leg_count': len(props)}
