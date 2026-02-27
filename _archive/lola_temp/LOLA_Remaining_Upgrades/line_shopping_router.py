# backend/routers/line_shopping_router.py
# Best available line across all books for a given prop
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database import get_db
from models import PropOdds
from typing import Optional

router = APIRouter(prefix='/api/shop', tags=['line_shopping'])

@router.get('/best-line')
def best_line(player_name: str, stat_category: str, side: str = Query(default='over'),
              db: Session = Depends(get_db)):
    props = db.query(PropOdds).filter(
        PropOdds.player_name.ilike(f'%{player_name}%'),
        PropOdds.stat_category == stat_category
    ).all()
    if not props:
        return {'error': 'No lines found'}
    books = []
    for p in props:
        odds = p.over_odds if side == 'over' else p.under_odds
        books.append({'book': p.book, 'line': p.line, 'odds': odds,
                      'implied_prob': round(100 / (odds + 100) * 100, 1) if odds and odds > 0 else round(abs(odds) / (abs(odds) + 100) * 100, 1) if odds else None})
    if side == 'over':
        best = max(books, key=lambda x: (x['line'] or 0))
    else:
        best = min(books, key=lambda x: (x['line'] or 999))
    return {
        'player': player_name, 'stat': stat_category, 'side': side,
        'best_book': best['book'], 'best_line': best['line'], 'best_odds': best['odds'],
        'all_books': sorted(books, key=lambda x: x['line'] or 0, reverse=(side == 'over'))
    }

@router.get('/slate-shopping')
def slate_shopping(sport: Optional[str] = None, db: Session = Depends(get_db)):
    from sqlalchemy import func
    q = db.query(
        PropOdds.player_name,
        PropOdds.stat_category,
        func.count(PropOdds.book.distinct()).label('book_count'),
        func.max(PropOdds.line).label('best_over_line'),
        func.min(PropOdds.line).label('best_under_line')
    )
    if sport:
        q = q.filter(PropOdds.sport == sport)
    rows = q.group_by(PropOdds.player_name, PropOdds.stat_category).having(
        func.count(PropOdds.book.distinct()) >= 2
    ).limit(50).all()
    return [{
        'player': r.player_name, 'stat': r.stat_category,
        'books_available': r.book_count,
        'best_over_line': r.best_over_line,
        'best_under_line': r.best_under_line,
        'line_spread': round((r.best_over_line or 0) - (r.best_under_line or 0), 1)
    } for r in rows]
