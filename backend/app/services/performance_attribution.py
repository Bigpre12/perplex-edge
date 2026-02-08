"""
Performance Attribution Service - Factor breakdown for picks
"""

from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
from sqlalchemy.orm import selectinload

from app.models import ModelPick, Player, Team, Game, Market

@dataclass
class AttributionFactor:
    """Individual factor contributing to pick prediction."""
    factor_name: str
    contribution: float  # -1 to 1 (negative = reduces confidence, positive = increases)
    weight: float  # Importance weight (0-1)
    rationale: str
    value: Any  # Actual value of the factor

class PerformanceAttribution:
    """Analyzes and attributes performance to individual factors."""
    
    def __init__(self):
        self.factor_weights = {
            "recent_performance": 0.25,
            "opponent_context": 0.20,
            "game_context": 0.15,
            "market_factors": 0.15,
            "player_context": 0.15,
            "historical_trends": 0.10
        }
    
    def analyze_recent_performance(
        self,
        recent_5g_avg: float,
        recent_10g_avg: float,
        season_avg: float,
        line_value: float,
        side: str
    ) -> AttributionFactor:
        """Analyze recent performance contribution."""
        
        # Calculate performance vs line
        if side.lower() == "over":
            performance_vs_line_5g = (recent_5g_avg - line_value) / line_value if line_value > 0 else 0
            performance_vs_line_10g = (recent_10g_avg - line_value) / line_value if line_value > 0 else 0
        else:
            performance_vs_line_5g = (line_value - recent_5g_avg) / line_value if line_value > 0 else 0
            performance_vs_line_10g = (line_value - recent_10g_avg) / line_value if line_value > 0 else 0
        
        # Weight recent performance more heavily
        weighted_performance = (performance_vs_line_5g * 0.6) + (performance_vs_line_10g * 0.4)
        
        # Compare to season average
        season_comparison = (recent_10g_avg - season_avg) / season_avg if season_avg > 0 else 0
        
        # Calculate contribution
        contribution = (weighted_performance * 0.7) + (season_comparison * 0.3)
        contribution = max(-1, min(1, contribution))  # Clamp to [-1, 1]
        
        # Generate rationale
        if contribution > 0.2:
            rationale = f"Strong recent performance: {recent_5g_avg:.1f} vs {line_value} {side}"
        elif contribution > 0:
            rationale = f"Positive recent performance: {recent_5g_avg:.1f} vs {line_value} {side}"
        elif contribution > -0.2:
            rationale = f"Below recent performance: {recent_5g_avg:.1f} vs {line_value} {side}"
        else:
            rationale = f"Poor recent performance: {recent_5g_avg:.1f} vs {line_value} {side}"
        
        return AttributionFactor(
            factor_name="recent_performance",
            contribution=contribution,
            weight=self.factor_weights["recent_performance"],
            rationale=rationale,
            value={
                "recent_5g_avg": recent_5g_avg,
                "recent_10g_avg": recent_10g_avg,
                "season_avg": season_avg,
                "line_value": line_value,
                "side": side
            }
        )
    
    def analyze_opponent_context(
        self,
        opponent_defensive_rating: float,
        opponent_pace: float,
        stat_type: str,
        player_position: str
    ) -> AttributionFactor:
        """Analyze opponent context contribution."""
        
        # Different stats are affected differently by opponent
        stat_impact = {
            "PTS": {"PG": 0.3, "SG": 0.4, "SF": 0.5, "PF": 0.6, "C": 0.7},
            "AST": {"PG": 0.6, "SG": 0.4, "SF": 0.3, "PF": 0.2, "C": 0.1},
            "REB": {"PG": 0.2, "SG": 0.3, "SF": 0.4, "PF": 0.6, "C": 0.8},
            "BLK": {"PG": 0.1, "SG": 0.1, "SF": 0.2, "PF": 0.4, "C": 0.7},
        }
        
        # Get impact factor for this stat and position
        impact_factor = stat_impact.get(stat_type, {}).get(player_position, 0.3)
        
        # Calculate opponent effect
        # Lower defensive rating = easier for offense (positive for over)
        # Higher pace = more possessions (positive for volume stats)
        defensive_effect = (1.0 - opponent_defensive_rating) * impact_factor
        pace_effect = (opponent_pace - 100) / 100 * 0.3  # Normalized around 100
        
        contribution = defensive_effect + pace_effect
        contribution = max(-1, min(1, contribution))
        
        # Generate rationale
        if contribution > 0.3:
            rationale = f"Favorable matchup: weak defense ({opponent_defensive_rating:.2f}) and good pace ({opponent_pace:.1f})"
        elif contribution > 0:
            rationale = f"Neutral matchup: defense ({opponent_defensive_rating:.2f}) and pace ({opponent_pace:.1f})"
        elif contribution > -0.3:
            rationale = f"Tough matchup: strong defense ({opponent_defensive_rating:.2f})"
        else:
            rationale = f"Very tough matchup: elite defense ({opponent_defensive_rating:.2f})"
        
        return AttributionFactor(
            factor_name="opponent_context",
            contribution=contribution,
            weight=self.factor_weights["opponent_context"],
            rationale=rationale,
            value={
                "opponent_defensive_rating": opponent_defensive_rating,
                "opponent_pace": opponent_pace,
                "stat_type": stat_type,
                "player_position": player_position,
                "impact_factor": impact_factor
            }
        )
    
    def analyze_game_context(
        self,
        is_home_game: bool,
        back_to_back: bool,
        travel_distance: float,
        altitude: float,
        days_since_last_game: int
    ) -> AttributionFactor:
        """Analyze game context contribution."""
        
        contribution = 0.0
        
        # Home court advantage
        if is_home_game:
            contribution += 0.1
        else:
            contribution -= 0.05
        
        # Back-to-back fatigue
        if back_to_back:
            contribution -= 0.1
        
        # Travel fatigue
        if travel_distance > 1000:  # Long travel
            contribution -= 0.08
        elif travel_distance > 500:  # Medium travel
            contribution -= 0.03
        
        # Altitude effects
        if altitude > 3000:  # High altitude (Denver, Salt Lake City)
            contribution -= 0.05
        elif altitude > 1000:  # Moderate altitude
            contribution -= 0.02
        
        # Rest days
        if days_since_last_game >= 3:
            contribution += 0.05
        elif days_since_last_game == 1:
            contribution -= 0.03
        
        contribution = max(-1, min(1, contribution))
        
        # Generate rationale
        context_factors = []
        if is_home_game:
            context_factors.append("home game")
        if back_to_back:
            context_factors.append("back-to-back")
        if travel_distance > 500:
            context_factors.append(f"travel ({travel_distance:.0f} miles)")
        if altitude > 1000:
            context_factors.append(f"altitude ({altitude:.0f} ft)")
        if days_since_last_game >= 3:
            context_factors.append("well-rested")
        elif days_since_last_game == 1:
            context_factors.append("short rest")
        
        rationale = "Game context: " + ", ".join(context_factors)
        
        return AttributionFactor(
            factor_name="game_context",
            contribution=contribution,
            weight=self.factor_weights["game_context"],
            rationale=rationale,
            value={
                "is_home_game": is_home_game,
                "back_to_back": back_to_back,
                "travel_distance": travel_distance,
                "altitude": altitude,
                "days_since_last_game": days_since_last_game
            }
        )
    
    def analyze_market_factors(
        self,
        opening_line: float,
        current_line: float,
        line_movement: float,
        market_limit: int,
        sharp_money_indicator: float
    ) -> AttributionFactor:
        """Analyze market factors contribution."""
        
        contribution = 0.0
        
        # Line movement (follow sharp money)
        if sharp_money_indicator > 0.3:  # Sharp under movement
            contribution += 0.1
        elif sharp_money_indicator < -0.3:  # Sharp over movement
            contribution -= 0.1
        
        # Market limit (higher limits = sharper market)
        if market_limit > 10000:
            contribution += 0.05  # Sharp market
        elif market_limit < 2000:
            contribution -= 0.05  # Soft market
        
        # Line stability
        line_stability = abs(line_movement)
        if line_stability < 2:  # Stable line
            contribution += 0.03
        elif line_stability > 10:  # Volatile line
            contribution -= 0.03
        
        contribution = max(-1, min(1, contribution))
        
        # Generate rationale
        market_factors = []
        if abs(sharp_money_indicator) > 0.3:
            market_factors.append("sharp money movement")
        if market_limit > 10000:
            market_factors.append("high-limit market")
        elif market_limit < 2000:
            market_factors.append("low-limit market")
        if line_stability < 2:
            market_factors.append("stable line")
        elif line_stability > 10:
            market_factors.append("volatile line")
        
        rationale = "Market factors: " + ", ".join(market_factors)
        
        return AttributionFactor(
            factor_name="market_factors",
            contribution=contribution,
            weight=self.factor_weights["market_factors"],
            rationale=rationale,
            value={
                "opening_line": opening_line,
                "current_line": current_line,
                "line_movement": line_movement,
                "market_limit": market_limit,
                "sharp_money_indicator": sharp_money_indicator
            }
        )
    
    def analyze_player_context(
        self,
        injury_status: str,
        lineup_status: str,
        rest_days: int,
        minutes_last_game: int
    ) -> AttributionFactor:
        """Analyze player context contribution."""
        
        contribution = 0.0
        
        # Injury status
        if injury_status == "healthy":
            contribution += 0.05
        elif injury_status == "questionable":
            contribution -= 0.1
        elif injury_status == "out":
            contribution -= 0.5
        
        # Lineup status
        if lineup_status == "confirmed":
            contribution += 0.03
        elif lineup_status == "probable":
            contribution += 0.01
        elif lineup_status == "questionable":
            contribution -= 0.05
        
        # Rest days
        if rest_days >= 3:
            contribution += 0.05
        elif rest_days == 0:
            contribution -= 0.08
        
        # Minutes last game (conditioning)
        if minutes_last_game >= 30:
            contribution += 0.03
        elif minutes_last_game <= 15:
            contribution -= 0.05
        
        contribution = max(-1, min(1, contribution))
        
        # Generate rationale
        player_factors = []
        if injury_status == "healthy":
            player_factors.append("healthy")
        elif injury_status != "healthy":
            player_factors.append(f"injury: {injury_status}")
        
        if lineup_status == "confirmed":
            player_factors.append("confirmed starter")
        elif lineup_status != "confirmed":
            player_factors.append(f"lineup: {lineup_status}")
        
        if rest_days >= 3:
            player_factors.append("well-rested")
        elif rest_days == 0:
            player_factors.append("no rest")
        
        if minutes_last_game >= 30:
            player_factors.append("good minutes")
        elif minutes_last_game <= 15:
            player_factors.append("limited minutes")
        
        rationale = "Player context: " + ", ".join(player_factors)
        
        return AttributionFactor(
            factor_name="player_context",
            contribution=contribution,
            weight=self.factor_weights["player_context"],
            rationale=rationale,
            value={
                "injury_status": injury_status,
                "lineup_status": lineup_status,
                "rest_days": rest_days,
                "minutes_last_game": minutes_last_game
            }
        )
    
    def calculate_attribution_score(
        self,
        factors: List[AttributionFactor]
    ) -> Dict[str, Any]:
        """Calculate overall attribution score from factors."""
        
        weighted_score = 0.0
        total_weight = 0.0
        
        positive_factors = []
        negative_factors = []
        
        for factor in factors:
            weighted_contribution = factor.contribution * factor.weight
            weighted_score += weighted_contribution
            total_weight += factor.weight
            
            if factor.contribution > 0.1:
                positive_factors.append(factor)
            elif factor.contribution < -0.1:
                negative_factors.append(factor)
        
        # Normalize score
        if total_weight > 0:
            normalized_score = weighted_score / total_weight
        else:
            normalized_score = 0.0
        
        # Convert to 0-1 scale
        attribution_score = (normalized_score + 1) / 2
        
        return {
            "attribution_score": round(attribution_score, 3),
            "weighted_score": round(weighted_score, 3),
            "total_weight": round(total_weight, 3),
            "positive_factors": [
                {
                    "factor": f.factor_name,
                    "contribution": round(f.contribution, 3),
                    "weight": round(f.weight, 3),
                    "rationale": f.rationale
                }
                for f in positive_factors
            ],
            "negative_factors": [
                {
                    "factor": f.factor_name,
                    "contribution": round(f.contribution, 3),
                    "weight": round(f.weight, 3),
                    "rationale": f.rationale
                }
                for f in negative_factors
            ],
            "all_factors": [
                {
                    "factor": f.factor_name,
                    "contribution": round(f.contribution, 3),
                    "weight": round(f.weight, 3),
                    "rationale": f.rationale,
                    "value": f.value
                }
                for f in factors
            ]
        }
    
    async def analyze_pick_attribution(
        self,
        db: AsyncSession,
        pick_id: int
    ) -> Dict[str, Any]:
        """Analyze performance attribution for a specific pick."""
        
        # Get pick details
        query = select(ModelPick).options(
            selectinload(ModelPick.player),
            selectinload(ModelPick.market),
            selectinload(ModelPick.game)
        ).where(ModelPick.id == pick_id)
        
        result = await db.execute(query)
        pick = result.scalar_one_or_none()
        
        if not pick:
            return {
                "status": "error",
                "message": f"Pick {pick_id} not found"
            }
        
        # Mock data for analysis (in production, this would come from actual data sources)
        factors = []
        
        # Recent performance
        factors.append(self.analyze_recent_performance(
            recent_5g_avg=15.5,
            recent_10g_avg=15.2,
            season_avg=14.8,
            line_value=pick.line_value,
            side=pick.side
        ))
        
        # Opponent context
        factors.append(self.analyze_opponent_context(
            opponent_defensive_rating=0.45,
            opponent_pace=98.5,
            stat_type=pick.market.stat_type if pick.market else "unknown",
            player_position="PG"  # Would get from player data
        ))
        
        # Game context
        factors.append(self.analyze_game_context(
            is_home_game=True,
            back_to_back=False,
            travel_distance=250,
            altitude=500,
            days_since_last_game=2
        ))
        
        # Market factors
        factors.append(self.analyze_market_factors(
            opening_line=pick.line_value,
            current_line=pick.line_value,
            line_movement=0.0,
            market_limit=5000,
            sharp_money_indicator=0.0
        ))
        
        # Player context
        factors.append(self.analyze_player_context(
            injury_status="healthy",
            lineup_status="confirmed",
            rest_days=2,
            minutes_last_game=28
        ))
        
        # Calculate attribution score
        attribution_result = self.calculate_attribution_score(factors)
        
        return {
            "status": "success",
            "pick_id": pick_id,
            "player_name": pick.player.name if pick.player else "Unknown",
            "stat_type": pick.market.stat_type if pick.market else "unknown",
            "line_value": pick.line_value,
            "side": pick.side,
            "attribution": attribution_result,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
    
    async def analyze_batch_attribution(
        self,
        db: AsyncSession,
        sport_id: int = 30,
        limit: int = 50
    ) -> Dict[str, Any]:
        """Analyze performance attribution for multiple picks."""
        
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=24)
        
        # Get recent picks
        query = select(ModelPick).options(
            selectinload(ModelPick.player),
            selectinload(ModelPick.market)
        ).where(
            and_(
                ModelPick.sport_id == sport_id,
                ModelPick.generated_at >= cutoff_time
            )
        ).order_by(desc(ModelPick.generated_at)).limit(limit)
        
        result = await db.execute(query)
        picks = result.scalars().all()
        
        attribution_results = []
        
        for pick in picks:
            try:
                attribution = await self.analyze_pick_attribution(db, pick.id)
                if attribution["status"] == "success":
                    attribution_results.append(attribution)
            except Exception as e:
                print(f"Error analyzing pick {pick.id}: {e}")
                continue
        
        # Calculate aggregate statistics
        if attribution_results:
            avg_attribution_score = sum(r["attribution"]["attribution_score"] for r in attribution_results) / len(attribution_results)
            
            # Factor frequency analysis
            factor_frequency = {}
            for result in attribution_results:
                for factor in result["attribution"]["all_factors"]:
                    factor_name = factor["factor"]
                    if factor_name not in factor_frequency:
                        factor_frequency[factor_name] = {
                            "count": 0,
                            "avg_contribution": 0.0
                        }
                    factor_frequency[factor_name]["count"] += 1
                    factor_frequency[factor_name]["avg_contribution"] += factor["contribution"]
            
            # Calculate averages
            for factor_name in factor_frequency:
                count = factor_frequency[factor_name]["count"]
                factor_frequency[factor_name]["avg_contribution"] /= count
        else:
            avg_attribution_score = 0.0
            factor_frequency = {}
        
        return {
            "status": "success",
            "sport_id": sport_id,
            "total_picks": len(picks),
            "analyzed_picks": len(attribution_results),
            "avg_attribution_score": round(avg_attribution_score, 3),
            "factor_frequency": factor_frequency,
            "attribution_results": attribution_results,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
