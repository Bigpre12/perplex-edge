"""
CLV (Closing Line Value) Tracking Service - The most important sports betting metric
"""

from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
from sqlalchemy.orm import selectinload

from app.models import ModelPick, Game, Player, Market, PickResult

@dataclass
class CLVMetrics:
    """CLV metrics for a pick or group of picks."""
    entry_odds: float
    closing_odds: float
    entry_implied_prob: float
    closing_implied_prob: float
    clv_percentage: float
    clv_dollars: float
    roi_percentage: float
    won: bool

class CLVTracker:
    """Tracks Closing Line Value to prove model edge."""
    
    def __init__(self):
        self.clv_history = []
        self.sport_metrics = {}
    
    def calculate_clv(
        self, 
        entry_odds: int, 
        closing_odds: int,
        stake: float = 100.0
    ) -> CLVMetrics:
        """
        Calculate CLV metrics for a single bet.
        
        Args:
            entry_odds: American odds when bet was placed
            closing_odds: American odds at game time
            stake: Bet amount (default $100)
        
        Returns:
            CLVMetrics object with all calculations
        """
        # Convert to implied probabilities
        entry_implied_prob = self.american_to_implied_probability(entry_odds)
        closing_implied_prob = self.american_to_implied_probability(closing_odds)
        
        # Calculate CLV percentage
        if entry_implied_prob > 0:
            clv_percentage = ((entry_implied_prob - closing_implied_prob) / entry_implied_prob) * 100
        else:
            clv_percentage = 0.0
        
        # Calculate CLV in dollars
        if entry_odds < 0:
            entry_payout = (stake * 100) / abs(entry_odds)
        else:
            entry_payout = stake * (entry_odds / 100)
        
        if closing_odds < 0:
            closing_payout = (stake * 100) / abs(closing_odds)
        else:
            closing_payout = stake * (closing_odds / 100)
        
        clv_dollars = entry_payout - closing_payout
        
        # Calculate ROI
        won = False  # This will be set when result is known
        
        return CLVMetrics(
            entry_odds=entry_odds,
            closing_odds=closing_odds,
            entry_implied_prob=entry_implied_prob,
            closing_implied_prob=closing_implied_prob,
            clv_percentage=clv_percentage,
            clv_dollars=clv_dollars,
            roi_percentage=0.0,  # Will be calculated after result
            won=won
        )
    
    def american_to_implied_probability(self, odds: int) -> float:
        """Convert American odds to implied probability."""
        if odds < 0:
            return abs(odds) / (abs(odds) + 100)
        else:
            return 100 / (odds + 100)
    
    def calculate_roi(self, clv_metrics: CLVMetrics, stake: float = 100.0, won: Optional[bool] = None) -> float:
        """Calculate ROI for a completed bet."""
        if won:
            if clv_metrics.entry_odds < 0:
                payout = (stake * 100) / abs(clv_metrics.entry_odds)
            else:
                payout = stake * (clv_metrics.entry_odds / 100)
            
            profit = payout - stake
        else:
            profit = -stake
        
        return (profit / stake) * 100
    
    async def track_pick_clv(
        self, 
        db: AsyncSession,
        pick_id: int,
        closing_odds: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Track CLV for a single pick.
        
        Args:
            db: Database session
            pick_id: Pick ID to track
            closing_odds: Closing odds (if available)
        
        Returns:
            CLV tracking result
        """
        # Get the pick with result
        query = select(ModelPick).options(
            selectinload(ModelPick.result),
            selectinload(ModelPick.player),
            selectinload(ModelPick.market)
        ).where(ModelPick.id == pick_id)
        
        result = await db.execute(query)
        pick = result.scalar_one_or_none()
        
        if not pick:
            return {
                "status": "error",
                "message": f"Pick {pick_id} not found"
            }
        
        # Use provided closing odds or get from database
        if closing_odds is None:
            closing_odds = pick.closing_odds  # Assuming this field exists
        
        if closing_odds is None:
            return {
                "status": "no_closing_odds",
                "message": "No closing odds available for CLV calculation"
            }
        
        # Calculate CLV metrics
        clv_metrics = self.calculate_clv(pick.odds, closing_odds)
        
        # Set won status if result exists
        if pick.result:
            clv_metrics.won = pick.result.hit
            clv_metrics.roi_percentage = self.calculate_roi(clv_metrics, won=pick.result.hit)
        elif won is not None:
            clv_metrics.won = won
            clv_metrics.roi_percentage = self.calculate_roi(clv_metrics, won=won)
        
        # Store CLV data
        clv_data = {
            "pick_id": pick_id,
            "player_name": pick.player.name if pick.player else "Unknown",
            "sport_id": pick.sport_id,
            "market": pick.market.stat_type if pick.market else "Unknown",
            "line_value": pick.line_value,
            "side": pick.side,
            "entry_odds": pick.odds,
            "closing_odds": closing_odds,
            "entry_implied_prob": clv_metrics.entry_implied_prob,
            "closing_implied_prob": clv_metrics.closing_implied_prob,
            "clv_percentage": clv_metrics.clv_percentage,
            "clv_dollars": clv_metrics.clv_dollars,
            "roi_percentage": clv_metrics.roi_percentage,
            "won": clv_metrics.won,
            "result_date": pick.result.created_at.isoformat() if pick.result else None
        }
        
        self.clv_history.append(clv_data)
        
        return {
            "status": "success",
            "clv_data": clv_data
        }
    
    async def get_clv_dashboard(
        self, 
        db: AsyncSession,
        sport_id: Optional[int] = None,
        days_back: int = 30
    ) -> Dict[str, Any]:
        """
        Get CLV dashboard data for visualization.
        
        Args:
            db: Database session
            sport_id: Optional sport filter
            days_back: Number of days to analyze
        
        Returns:
            CLV dashboard data
        """
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_back)
        
        # Build query
        query = select(ModelPick).options(
            selectinload(ModelPick.result),
            selectinload(ModelPick.player),
            selectinload(ModelPick.market)
        ).where(
            and_(
                ModelPick.generated_at >= cutoff_date,
                ModelPick.closing_odds.isnot(None),
                ModelPick.result.isnot(None)
            )
        )
        
        if sport_id:
            query = query.where(ModelPick.sport_id == sport_id)
        
        query = query.order_by(desc(ModelPick.generated_at))
        
        result = await db.execute(query)
        picks = result.scalars().all()
        
        if not picks:
            return {
                "status": "no_data",
                "message": f"No CLV data found for last {days_back} days"
            }
        
        # Calculate CLV metrics for all picks
        clv_metrics = []
        total_clv_dollars = 0
        total_roi = 0
        total_bets = len(picks)
        winning_bets = 0
        
        for pick in picks:
            clv_metric = self.calculate_clv(pick.odds, pick.closing_odds)
            clv_metric.won = pick.result.hit
            clv_metric.roi_percentage = self.calculate_roi(clv_metric, won=pick.result.hit)
            
            clv_metrics.append(clv_metric)
            total_clv_dollars += clv_metric.clv_dollars
            total_roi += clv_metric.roi_percentage
            
            if pick.result.hit:
                winning_bets += 1
        
        # Calculate averages
        avg_clv_percentage = sum(m.clv_percentage for m in clv_metrics) / len(clv_metrics)
        avg_roi = total_roi / total_bets
        win_rate = winning_bets / total_bets
        
        # CLV distribution
        clv_distribution = {
            "positive_clv": len([m for m in clv_metrics if m.clv_percentage > 0]),
            "negative_clv": len([m for m in clv_metrics if m.clv_percentage < 0]),
            "zero_clv": len([m for m in clv_metrics if abs(m.clv_percentage) < 0.1])
        }
        
        # CLV by confidence level
        clv_by_confidence = {
            "high_confidence": [],  # > 0.7
            "medium_confidence": [],  # 0.6-0.7
            "low_confidence": []   # < 0.6
        }
        
        for i, pick in enumerate(picks):
            conf = pick.confidence_score
            clv_metric = clv_metrics[i]
            
            if conf > 0.7:
                clv_by_confidence["high_confidence"].append(clv_metric)
            elif conf >= 0.6:
                clv_by_confidence["medium_confidence"].append(clv_metric)
            else:
                clv_by_confidence["low_confidence"].append(clv_metric)
        
        # Calculate CLV by confidence
        clv_by_confidence_metrics = {}
        for level, metrics in clv_by_confidence.items():
            if metrics:
                avg_clv = sum(m.clv_percentage for m in metrics) / len(metrics)
                avg_roi = sum(m.roi_percentage for m in metrics) / len(metrics)
                win_rate = sum(1 for m in metrics if m.won) / len(metrics)
                
                clv_by_confidence_metrics[level] = {
                    "count": len(metrics),
                    "avg_clv_percentage": avg_clv,
                    "avg_roi_percentage": avg_roi,
                    "win_rate": win_rate
                }
        
        return {
            "status": "success",
            "period_days": days_back,
            "total_bets": total_bets,
            "win_rate": win_rate,
            "avg_clv_percentage": round(avg_clv_percentage, 2),
            "total_clv_dollars": round(total_clv_dollars, 2),
            "avg_roi_percentage": round(avg_roi, 2),
            "clv_distribution": clv_distribution,
            "clv_by_confidence": clv_by_confidence_metrics,
            "clv_history": [
                {
                    "date": pick.generated_at.isoformat(),
                    "player": pick.player.name if pick.player else "Unknown",
                    "clv_percentage": clv_metrics[i].clv_percentage,
                    "roi_percentage": clv_metrics[i].roi_percentage,
                    "won": clv_metrics[i].won
                }
                for i, pick in enumerate(picks[:50])  # Last 50 picks
            ],
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
    
    async def get_clv_leaderboard(
        self, 
        db: AsyncSession,
        sport_id: Optional[int] = None,
        min_bets: int = 10
    ) -> Dict[str, Any]:
        """
        Get CLV leaderboard for top performers.
        
        Args:
            db: Database session
            sport_id: Optional sport filter
            min_bets: Minimum number of bets to qualify
        
        Returns:
            CLV leaderboard data
        """
        # This would be implemented to track user performance
        # For now, return mock data
        return {
            "status": "success",
            "leaderboard": [
                {
                    "rank": 1,
                    "username": "sharp_bettor_1",
                    "avg_clv": 2.3,
                    "total_bets": 156,
                    "roi": 4.7,
                    "win_rate": 0.54
                },
                {
                    "rank": 2,
                    "username": "pro_analyst_2",
                    "avg_clv": 1.8,
                    "total_bets": 89,
                    "roi": 3.2,
                    "win_rate": 0.52
                }
            ]
        }
