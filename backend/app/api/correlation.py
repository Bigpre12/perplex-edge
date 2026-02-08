"""
Correlation Analysis API - Same - game parlay correlation analysis
"""

from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.correlation_analyzer import CorrelationAnalyzer

router = APIRouter(prefix = " / api / correlation", tags = ["correlation"])

@router.get(" / analyze / {game_id}")
async def analyze_game_correlations(game_id: int,
 db: AsyncSession = Depends(get_db)):
 """Analyze correlations between all picks in a game."""
 try:
 analyzer = CorrelationAnalyzer()
 correlations = await analyzer.analyze_same_game_correlations(db, game_id)
 return correlations
 except Exception as e:
 return {
 "status": "error",
 "message": str(e),
 "timestamp": datetime.now(timezone.utc).isoformat()
 }

@router.post(" / parlay - adjustment")
async def calculate_parlay_adjustment(correlations: list = Query(..., description = "List of correlation data"),
 db: AsyncSession = Depends(get_db)):
 """Calculate correlation adjustment for parlay probability."""
 try:
 analyzer = CorrelationAnalyzer()
 adjustment = analyzer.calculate_parlay_correlation_adjustment(correlations)
 return {
 "status": "success",
 "correlation_adjustment": adjustment,
 "correlations_analyzed": len(correlations)
 }
 except Exception as e:
 return {
 "status": "error",
 "message": str(e),
 "timestamp": datetime.now(timezone.utc).isoformat()
 }
