"""
Line Shopping API - Find best odds across sportsbooks
"""

from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.multi_book_shopper import MultiBookShopper

router = APIRouter(prefix = " / api / line - shopping", tags = ["line - shopping"])

@router.get(" / pick / {pick_id}")
async def find_best_odds_for_pick(pick_id: int,
 model_prob: float = Query(default = 0.55, description = "Model probability"),
 db: AsyncSession = Depends(get_db)):
 """Find best odds across all sportsbooks for a specific pick."""
 try:
 shopper = MultiBookShopper()
 best_odds = await shopper.find_best_odds_for_pick(db, pick_id, model_prob)
 return {
 "status": "success",
 "best_odds": best_odds
 }
 except Exception as e:
 return {
 "status": "error",
 "message": str(e),
 "timestamp": datetime.now(timezone.utc).isoformat()
 }

@router.get(" / game / {game_id}")
async def find_best_odds_for_game(game_id: int,
 db: AsyncSession = Depends(get_db)):
 """Find best odds for all picks in a game."""
 try:
 shopper = MultiBookShopper()
 game_odds = await shopper.find_best_odds_for_game(db, game_id)
 return game_odds
 except Exception as e:
 return {
 "status": "error",
 "message": str(e),
 "timestamp": datetime.now(timezone.utc).isoformat()
 }

@router.get(" / summary / {sport_id}")
async def get_line_shopping_summary(sport_id: int = Path(description = "Sport ID"),
 hours_back: int = Query(default = 24, description = "Hours to look back"),
 db: AsyncSession = Depends(get_db)):
 """Get line shopping summary for recent picks."""
 try:
 shopper = MultiBookShopper()
 summary = await shopper.get_line_shopping_summary(db, sport_id, hours_back)
 return summary
 except Exception as e:
 return {
 "status": "error",
 "message": str(e),
 "timestamp": datetime.now(timezone.utc).isoformat()
 }
