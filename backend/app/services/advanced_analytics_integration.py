"""
Advanced Analytics Integration Service - Ties together all Phase 2 features
"""

from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, and_
from sqlalchemy.orm import selectinload

from app.models import ModelPick, Game, Player, Market, Team
from app.services.line_movement_tracker import LineMovementTracker
from app.services.correlation_analyzer import CorrelationAnalyzer
from app.services.multi_book_shopper import MultiBookShopper
from app.services.performance_attribution import PerformanceAttribution
from app.services.clv_tracker import CLVTracker
from app.services.probability_calibration import ProbabilityCalibrator

@dataclass
class AdvancedAnalyticsResult:
    """Complete advanced analytics result for a pick."""
    pick_id: int
    player_name: str
    stat_type: str
    line_value: float
    side: str
    
    # Core metrics
    calibrated_probability: float
    expected_value: float
    confidence_score: float
    
    # Line movement
    line_movement_data: Dict[str, Any]
    sharp_money_indicator: float
    
    # Multi-book shopping
    best_book_odds: float
    best_book_name: str
    ev_improvement: float
    arbitrage_opportunity: bool
    
    # Performance attribution
    attribution_score: float
    attribution_factors: List[Dict[str, Any]]
    
    # CLV tracking
    clv_potential: float
    roi_estimate: float

class AdvancedAnalyticsIntegration:
    """Integrates all advanced analytics features for comprehensive analysis."""
    
    def __init__(self):
        self.line_movement_tracker = LineMovementTracker()
        self.correlation_analyzer = CorrelationAnalyzer()
        self.multi_book_shopper = MultiBookShopper()
        self.performance_attribution = PerformanceAttribution()
        self.clv_tracker = CLVTracker()
        self.probability_calibrator = ProbabilityCalibrator()
    
    async def analyze_pick_comprehensive(
        self,
        db: AsyncSession,
        pick_id: int
    ) -> AdvancedAnalyticsResult:
        """Perform comprehensive analysis of a single pick."""
        
        # Get pick details
        query = select(ModelPick).options(
            selectinload(ModelPick.player),
            selectinload(ModelPick.market),
            selectinload(ModelPick.game)
        ).where(ModelPick.id == pick_id)
        
        result = await db.execute(query)
        pick = result.scalar_one_or_none()
        
        if not pick:
            raise ValueError(f"Pick {pick_id} not found")
        
        # 1. Probability Calibration
        implied_prob = self.multi_book_shopper.american_to_implied_prob(int(pick.odds))
        calibrated_prob = self.probability_calibrator.calibrate_probability(
            pick.model_probability,
            implied_prob,
            sample_size=10,
            market_type="player_props"
        )
        
        # 2. Line Movement Analysis
        line_movement_data = self.line_movement_tracker.calculate_line_movement(
            pick.opening_odds if pick.opening_odds else pick.odds,
            pick.odds
        )
        
        # 3. Multi-Book Shopping
        try:
            best_odds_result = await self.multi_book_shopper.find_best_odds_for_pick(
                db, pick_id, calibrated_prob
            )
            best_book_odds = best_odds_result.best_odds
            best_book_name = best_odds_result.best_book
            ev_improvement = best_odds_result.ev_improvement
            arbitrage_opportunity = best_odds_result.arbitrage_opportunity
        except:
            # Fallback to current odds
            best_book_odds = pick.odds
            best_book_name = "Current Book"
            ev_improvement = 0.0
            arbitrage_opportunity = False
        
        # 4. Performance Attribution
        try:
            attribution_result = await self.performance_attribution.analyze_pick_attribution(db, pick_id)
            attribution_score = attribution_result.get("attribution", {}).get("attribution_score", 0.5)
            attribution_factors = attribution_result.get("attribution", {}).get("all_factors", [])
        except:
            attribution_score = 0.5
            attribution_factors = []
        
        # 5. CLV Potential (mock calculation)
        clv_potential = (best_book_odds - pick.odds) / abs(pick.odds) * 100 if pick.odds != 0 else 0
        roi_estimate = calibrated_prob * ev_improvement
        
        return AdvancedAnalyticsResult(
            pick_id=pick_id,
            player_name=pick.player.name if pick.player else "Unknown",
            stat_type=pick.market.stat_type if pick.market else "Unknown",
            line_value=pick.line_value,
            side=pick.side,
            
            calibrated_probability=calibrated_prob,
            expected_value=pick.expected_value,
            confidence_score=pick.confidence_score,
            
            line_movement_data=line_movement_data,
            sharp_money_indicator=line_movement_data.get("sharp_indicator", 0),
            
            best_book_odds=best_book_odds,
            best_book_name=best_book_name,
            ev_improvement=ev_improvement,
            arbitrage_opportunity=arbitrage_opportunity,
            
            attribution_score=attribution_score,
            attribution_factors=attribution_factors,
            
            clv_potential=clv_potential,
            roi_estimate=roi_estimate
        )
    
    async def analyze_game_comprehensive(
        self,
        db: AsyncSession,
        game_id: int
    ) -> Dict[str, Any]:
        """Perform comprehensive analysis of all picks in a game."""
        
        # Get all picks for this game
        query = select(ModelPick).options(
            selectinload(ModelPick.player),
            selectinload(ModelPick.market)
        ).where(ModelPick.game_id == game_id)
        
        result = await db.execute(query)
        picks = result.scalars().all()
        
        if len(picks) < 2:
            return {
                "status": "insufficient_picks",
                "message": f"Only {len(picks)} picks found for game {game_id}"
            }
        
        # Analyze each pick
        comprehensive_results = []
        for pick in picks:
            try:
                result = await self.analyze_pick_comprehensive(db, pick.id)
                comprehensive_results.append(result)
            except Exception as e:
                print(f"Error analyzing pick {pick.id}: {e}")
                continue
        
        # Correlation analysis
        correlation_result = await self.correlation_analyzer.analyze_same_game_correlations(db, game_id)
        
        # Calculate game-level metrics
        avg_calibrated_prob = sum(r.calibrated_probability for r in comprehensive_results) / len(comprehensive_results)
        avg_ev_improvement = sum(r.ev_improvement for r in comprehensive_results) / len(comprehensive_results)
        total_arbitrage = sum(1 for r in comprehensive_results if r.arbitrage_opportunity)
        
        return {
            "status": "success",
            "game_id": game_id,
            "total_picks": len(picks),
            "analyzed_picks": len(comprehensive_results),
            "comprehensive_results": comprehensive_results,
            "correlation_analysis": correlation_result,
            "game_metrics": {
                "avg_calibrated_probability": round(avg_calibrated_prob, 3),
                "avg_ev_improvement": round(avg_ev_improvement, 4),
                "total_arbitrage_opportunities": total_arbitrage,
                "correlation_adjustment": self.correlation_analyzer.calculate_parlay_correlation_adjustment(
                    correlation_result.get("correlations", [])
                )
            },
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
    
    async def get_analytics_summary(
        self,
        db: AsyncSession,
        sport_id: int = 30,
        hours_back: int = 24
    ) -> Dict[str, Any]:
        """Get comprehensive analytics summary for recent picks."""
        
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours_back)
        
        # Get recent picks
        query = select(ModelPick).options(
            selectinload(ModelPick.player),
            selectinload(ModelPick.market)
        ).where(
            and_(
                ModelPick.sport_id == sport_id,
                ModelPick.generated_at >= cutoff_time
            )
        ).order_by(desc(ModelPick.generated_at)).limit(50)
        
        result = await db.execute(query)
        picks = result.scalars().all()
        
        comprehensive_results = []
        for pick in picks:
            try:
                result = await self.analyze_pick_comprehensive(db, pick.id)
                comprehensive_results.append(result)
            except Exception as e:
                print(f"Error analyzing pick {pick.id}: {e}")
                continue
        
        # Calculate summary metrics
        if comprehensive_results:
            avg_calibrated_prob = sum(r.calibrated_probability for r in comprehensive_results) / len(comprehensive_results)
            avg_ev_improvement = sum(r.ev_improvement for r in comprehensive_results) / len(comprehensive_results)
            avg_attribution_score = sum(r.attribution_score for r in comprehensive_results) / len(comprehensive_results)
            total_arbitrage = sum(1 for r in comprehensive_results if r.arbitrage_opportunity)
            
            # Line movement summary
            sharp_moves = sum(1 for r in comprehensive_results if abs(r.sharp_money_indicator) > 0.5)
            steam_moves = sum(1 for r in comprehensive_results if r.line_movement_data.get("steam_move", False))
            
            # Best books summary
            best_books = {}
            for r in comprehensive_results:
                book = r.best_book_name
                if book not in best_books:
                    best_books[book] = 0
                best_books[book] += 1
        else:
            avg_calibrated_prob = 0
            avg_ev_improvement = 0
            avg_attribution_score = 0
            total_arbitrage = 0
            sharp_moves = 0
            steam_moves = 0
            best_books = {}
        
        return {
            "status": "success",
            "sport_id": sport_id,
            "analysis_period_hours": hours_back,
            "total_picks": len(picks),
            "analyzed_picks": len(comprehensive_results),
            "comprehensive_results": comprehensive_results[:10],  # Top 10 for brevity
            "summary_metrics": {
                "avg_calibrated_probability": round(avg_calibrated_prob, 3),
                "avg_ev_improvement": round(avg_ev_improvement, 4),
                "avg_attribution_score": round(avg_attribution_score, 3),
                "total_arbitrage_opportunities": total_arbitrage,
                "sharp_money_moves": sharp_moves,
                "steam_moves": steam_moves,
                "best_books_distribution": best_books
            },
            "feature_status": {
                "probability_calibration": "active",
                "line_movement_tracking": "active",
                "multi_book_shopping": "active",
                "correlation_analysis": "active",
                "performance_attribution": "active",
                "clv_tracking": "active"
            },
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
    
    async def optimize_parlay_with_analytics(
        self,
        db: AsyncSession,
        game_id: int,
        max_legs: int = 3
    ) -> Dict[str, Any]:
        """Optimize parlay using all advanced analytics."""
        
        # Get comprehensive game analysis
        game_analysis = await self.analyze_game_comprehensive(db, game_id)
        
        if game_analysis["status"] != "success":
            return game_analysis
        
        # Sort picks by comprehensive score
        def comprehensive_score(result):
            # Weight different factors
            ev_weight = 0.3
            attribution_weight = 0.25
            line_movement_weight = 0.2
            shopping_weight = 0.15
            clv_weight = 0.1
            
            score = (
                result.expected_value * ev_weight +
                result.attribution_score * attribution_weight +
                abs(result.sharp_money_indicator) * line_movement_weight +
                result.ev_improvement * shopping_weight +
                result.clv_potential * clv_weight
            )
            return score
        
        sorted_results = sorted(
            game_analysis["comprehensive_results"],
            key=comprehensive_score,
            reverse=True
        )
        
        # Select top picks for parlay
        parlay_picks = sorted_results[:max_legs]
        
        # Calculate correlation adjustment
        correlations = game_analysis["correlation_analysis"].get("correlations", [])
        correlation_adjustment = self.correlation_analyzer.calculate_parlay_correlation_adjustment(correlations)
        
        # Calculate parlay metrics
        total_ev = sum(p.expected_value for p in parlay_picks)
        total_ev_improvement = sum(p.ev_improvement for p in parlay_picks)
        avg_confidence = sum(p.confidence_score for p in parlay_picks) / len(parlay_picks)
        
        return {
            "status": "success",
            "game_id": game_id,
            "optimized_parlay": {
                "picks": [
                    {
                        "player": p.player_name,
                        "stat": p.stat_type,
                        "line": p.line_value,
                        "side": p.side,
                        "expected_value": p.expected_value,
                        "confidence": p.confidence_score,
                        "best_book": p.best_book_name,
                        "ev_improvement": p.ev_improvement,
                        "comprehensive_score": comprehensive_score(p)
                    }
                    for p in parlay_picks
                ],
                "parlay_metrics": {
                    "total_ev": round(total_ev, 4),
                    "total_ev_improvement": round(total_ev_improvement, 4),
                    "avg_confidence": round(avg_confidence, 3),
                    "correlation_adjustment": round(correlation_adjustment, 3),
                    "adjusted_ev": round(total_ev * correlation_adjustment, 4),
                    "arbitrage_opportunities": sum(1 for p in parlay_picks if p.arbitrage_opportunity)
                }
            },
            "optimization_factors": {
                "correlation_analysis": game_analysis["correlation_analysis"],
                "game_metrics": game_analysis["game_metrics"]
            },
            "generated_at": datetime.now(timezone.utc).isoformat()
        }

# Global integration instance
advanced_analytics_integration = AdvancedAnalyticsIntegration()
