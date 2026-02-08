"""
Pick Grading Pipeline - Automated grading of completed picks
"""

import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, update
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models import ModelPick, Game, Player, Market, PickResult
from app.services.odds_provider import odds_provider
from app.services.results_api import fetch_game_results

logger = logging.getLogger(__name__)

class PickGrader:
    """Automated grading system for completed picks."""
    
    def __init__(self):
        self.grading_window_hours = 4  # Grade games 4 hours after they end
        self.batch_size = 50  # Process picks in batches
    
    async def grade_completed_picks(self, db: AsyncSession) -> Dict[str, Any]:
        """
        Grade all ungraded completed picks.
        
        Args:
            db: Database session
        
        Returns:
            Grading results summary
        """
        try:
            # Get ungraded picks from completed games
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=self.grading_window_hours)
            
            query = select(ModelPick).options(
                selectinload(ModelPick.game),
                selectinload(ModelPick.player),
                selectinload(ModelPick.market)
            ).where(
                and_(
                    ModelPick.result_id.is_(None),  # Not yet graded
                    ModelPick.game_start_time < cutoff_time,  # Game should be completed
                    ModelPick.game_id.isnot_(None)
                )
            ).limit(self.batch_size)
            
            result = await db.execute(query)
            picks = result.scalars().all()
            
            if not picks:
                return {
                    "status": "no_picks_to_grade",
                    "message": f"No ungraded picks found from games before {cutoff_time}",
                    "picks_processed": 0
                }
            
            logger.info(f"[grader] Found {len(picks)} picks to grade")
            
            graded_count = 0
            error_count = 0
            
            for pick in picks:
                try:
                    await self.grade_single_pick(db, pick)
                    graded_count += 1
                except Exception as e:
                    logger.error(f"[grader] Error grading pick {pick.id}: {e}")
                    error_count += 1
                    continue
            
            await db.commit()
            
            return {
                "status": "success",
                "picks_processed": len(picks),
                "graded_count": graded_count,
                "error_count": error_count,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"[grader] Error in grading pipeline: {e}", exc_info=True)
            await db.rollback()
            return {
                "status": "error",
                "message": str(e),
                "picks_processed": 0
            }
    
    async def grade_single_pick(self, db: AsyncSession, pick: ModelPick) -> bool:
        """
        Grade a single pick against actual results.
        
        Args:
            db: Database session
            pick: ModelPick to grade
        
        Returns:
            True if grading successful, False otherwise
        """
        try:
            # Get actual game result
            game_result = await fetch_game_results(pick.game_id)
            if not game_result:
                logger.warning(f"[grader] No game result found for game {pick.game_id}")
                return False
            
            # Get closing odds
            closing_odds = await self.get_closing_odds(pick.market_id, pick.player_id, pick.line_value, pick.side)
            
            # Determine if pick won
            did_win = self.evaluate_pick_result(pick, game_result)
            
            # Calculate CLV
            clv_percentage = self.calculate_clv(pick.odds, closing_odds)
            
            # Create or update pick result
            pick_result = await self.get_or_create_result(db, pick)
            pick_result.result = "WIN" if did_win else "LOSE"
            pick_result.graded_at = datetime.now(timezone.utc)
            pick_result.actual_value = game_result.get(pick.player_id, {}).get(pick.market.stat_type, 0)
            
            # Update pick with CLV data
            pick.closing_odds = closing_odds
            pick.clv_percentage = clv_percentage
            
            logger.info(f"[grader] Graded pick {pick.id}: {pick_result.result} (CLV: {clv_percentage:.2f}%)")
            
            return True
            
        except Exception as e:
            logger.error(f"[grader] Error grading pick {pick.id}: {e}", exc_info=True)
            return False
    
    def evaluate_pick_result(self, pick: ModelPick, game_result: Dict[str, Any]) -> bool:
        """
        Evaluate if a pick won based on actual game results.
        
        Args:
            pick: ModelPick with prediction
            game_result: Actual game results
        
        Returns:
            True if pick won, False otherwise
        """
        try:
            player_stats = game_result.get(pick.player_id, {})
            actual_value = player_stats.get(pick.market.stat_type, 0)
            
            if pick.side.lower() == "over":
                return actual_value > pick.line_value
            elif pick.side.lower() == "under":
                return actual_value < pick.line_value
            else:
                logger.warning(f"[grader] Unknown side '{pick.side}' for pick {pick.id}")
                return False
                
        except Exception as e:
            logger.error(f"[grader] Error evaluating pick result: {e}")
            return False
    
    async def get_closing_odds(self, market_id: int, player_id: int, line_value: float, side: str) -> Optional[int]:
        """
        Get closing odds for a specific pick.
        
        Args:
            market_id: Market ID
            player_id: Player ID
            line_value: Line value
            side: Over/Under
        
        Returns:
            Closing odds as integer, or None if not found
        """
        try:
            # This would integrate with your odds provider
            # For now, return the original odds as placeholder
            # In production, you'd fetch the actual closing line
            closing_line = await odds_provider.get_closing_line(market_id, player_id, line_value, side)
            return closing_line.get('odds') if closing_line else None
            
        except Exception as e:
            logger.error(f"[grader] Error getting closing odds: {e}")
            return None
    
    def calculate_clv(self, entry_odds: int, closing_odds: int) -> float:
        """
        Calculate Closing Line Value percentage.
        
        Args:
            entry_odds: Odds when pick was made
            closing_odds: Odds at game time
        
        Returns:
            CLV percentage (positive = beat closing line)
        """
        try:
            if not entry_odds or not closing_odds:
                return 0.0
            
            # Convert to implied probabilities
            entry_prob = self.american_to_implied_prob(entry_odds)
            closing_prob = self.american_to_implied_prob(closing_odds)
            
            # Calculate CLV as percentage
            clv = ((entry_prob - closing_prob) / closing_prob) * 100
            
            return round(clv, 2)
            
        except Exception as e:
            logger.error(f"[grader] Error calculating CLV: {e}")
            return 0.0
    
    def american_to_implied_prob(self, odds: int) -> float:
        """Convert American odds to implied probability."""
        if odds > 0:
            return 100 / (odds + 100)
        else:
            return abs(odds) / (abs(odds) + 100)
    
    async def get_or_create_result(self, db: AsyncSession, pick: ModelPick) -> PickResult:
        """Get existing result or create new one."""
        result = await db.execute(
            select(PickResult).where(PickResult.pick_id == pick.id)
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            return existing
        else:
            new_result = PickResult(
                pick_id=pick.id,
                result="PENDING",
                graded_at=datetime.now(timezone.utc)
            )
            db.add(new_result)
            await db.flush()
            return new_result
    
    async def get_grading_statistics(self, db: AsyncSession, days_back: int = 30) -> Dict[str, Any]:
        """
        Get statistics about graded picks.
        
        Args:
            db: Database session
            days_back: Days to look back
        
        Returns:
            Grading statistics
        """
        try:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_back)
            
            # Get graded picks count
            total_graded = await db.execute(
                select(func.count(ModelPick.id))
                .join(ModelPick.result)
                .where(ModelPick.result.graded_at >= cutoff_date)
            )
            total_graded_count = total_graded.scalar()
            
            # Get win rate
            wins = await db.execute(
                select(func.count(ModelPick.id))
                .join(ModelPick.result)
                .where(
                    and_(
                        ModelPick.result.graded_at >= cutoff_date,
                        ModelPick.result.result == "WIN"
                    )
                )
            )
            wins_count = wins.scalar()
            
            # Get CLV statistics
            clv_stats = await db.execute(
                select(
                    func.avg(ModelPick.clv_percentage),
                    func.count(ModelPick.id)
                )
                .where(
                    and_(
                        ModelPick.result.graded_at >= cutoff_date,
                        ModelPick.clv_percentage.isnot(None)
                    )
                )
            )
            clv_avg, clv_count = clv_stats.first()
            
            win_rate = (wins_count / total_graded_count * 100) if total_graded_count > 0 else 0
            
            return {
                "period_days": days_back,
                "total_graded": total_graded_count,
                "wins": wins_count,
                "losses": total_graded_count - wins_count,
                "win_rate": round(win_rate, 2),
                "avg_clv": round(clv_avg or 0, 2),
                "clv_samples": clv_count or 0,
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"[grader] Error getting grading statistics: {e}")
            return {
                "error": str(e),
                "period_days": days_back
            }

# Global grader instance
pick_grader = PickGrader()

# Celery task for automated grading (if using Celery)
# @celery_app.task
async def grade_completed_picks_task():
    """Background task to grade completed picks."""
    async with get_db() as db:
        return await pick_grader.grade_completed_picks(db)

# Simple scheduler function
async def run_grading_pipeline():
    """Run the grading pipeline (call this from a scheduler)."""
    async with get_db() as db:
        result = await pick_grader.grade_completed_picks(db)
        logger.info(f"[grader] Pipeline completed: {result}")
        return result
