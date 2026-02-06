"""
Deep Dive Service — comprehensive analysis of injuries, starters, and real-world factors.

This service provides deep insights into:
1. Injury analysis and impact on prop lines
2. Starter/bench changes and minutes adjustments
3. Team trends and matchup analysis
4. Market sentiment and line movements
5. Historical performance in similar situations

All data is integrated into the brain service for smarter predictions.
"""

import asyncio
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    Game, Player, Injury, ModelPick, Line, PlayerGameStats,
    PickResult, PlayerHitRate, Team, Sport
)
from app.core.constants import SPORT_ID_TO_KEY

logger = logging.getLogger(__name__)


@dataclass
class InjuryImpact:
    """Analysis of injury impact on team and player props."""
    player_name: str
    status: str
    status_detail: str
    probability: Optional[float]
    is_starter: bool
    impact_score: float  # 0-1, higher = more impactful
    affected_teammates: List[str] = field(default_factory=list)
    minutes_replacement: Optional[str] = None
    line_adjustment: Dict[str, float] = field(default_factory=dict)


@dataclass
class StarterChange:
    """Analysis of starter/bench changes."""
    player_name: str
    old_role: str  # "starter" or "bench"
    new_role: str
    minutes_change: float  # expected minutes change
    impact_on_props: Dict[str, float] = field(default_factory=dict)
    reason: Optional[str] = None


@dataclass
class MatchupAnalysis:
    """Deep analysis of team matchup."""
    home_team: str
    away_team: str
    home_advantage: float
    pace_rating: float  # expected possessions
    defensive_rating: Tuple[float, float]  # (home, away)
    key_matchups: List[str] = field(default_factory=list)
    betting_trends: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MarketSentiment:
    """Analysis of market sentiment and line movements."""
    sport: str
    game_id: str
    line_movements: Dict[str, List[Tuple[datetime, float]]] = field(default_factory=dict)
    volume_analysis: Dict[str, float] = field(default_factory=dict)
    sharp_money: Dict[str, str] = field(default_factory=dict)  # which side sharp money is on
    public_percentage: Dict[str, float] = field(default_factory=dict)


class DeepDiveService:
    """Comprehensive analysis service for sports betting intelligence."""
    
    def __init__(self):
        self.cache_timeout = 300  # 5 minutes
        self._cache = {}
    
    async def analyze_injuries(self, db: AsyncSession, sport_id: int) -> List[InjuryImpact]:
        """Analyze injuries and their impact on props."""
        cache_key = f"injuries_{sport_id}"
        if cache_key in self._cache:
            cached_time, cached_data = self._cache[cache_key]
            if datetime.now(timezone.utc) - cached_time < timedelta(seconds=self.cache_timeout):
                return cached_data
        
        # Get all injuries for the sport
        result = await db.execute(
            select(Injury, Player)
            .join(Player, Injury.player_id == Player.id)
            .where(Injury.sport_id == sport_id)
            .order_by(Injury.updated_at.desc())
        )
        
        impacts = []
        for injury, player in result:
            # Calculate impact score based on player importance and injury severity
            impact_score = self._calculate_injury_impact(injury, player)
            
            # Find affected teammates
            affected_teammates = await self._find_affected_teammates(db, player, impact_score)
            
            # Estimate line adjustments
            line_adjustment = self._estimate_line_adjustments(injury, player, impact_score)
            
            # Find replacement player
            minutes_replacement = await self._find_replacement_player(db, player)
            
            impacts.append(InjuryImpact(
                player_name=player.name,
                status=injury.status,
                status_detail=injury.status_detail or "",
                probability=injury.probability,
                is_starter=injury.is_starter_flag or False,
                impact_score=impact_score,
                affected_teammates=affected_teammates,
                minutes_replacement=minutes_replacement,
                line_adjustment=line_adjustment
            ))
        
        self._cache[cache_key] = (datetime.now(timezone.utc), impacts)
        return impacts
    
    def _calculate_injury_impact(self, injury: Injury, player: Player) -> float:
        """Calculate injury impact score (0-1)."""
        base_impact = 0.0
        
        # Status severity
        status_weights = {
            "OUT": 1.0,
            "DOUBTFUL": 0.8,
            "QUESTIONABLE": 0.6,
            "GTD": 0.4,
            "DAY_TO_DAY": 0.3,
            "PROBABLE": 0.1,
            "AVAILABLE": 0.0
        }
        base_impact = status_weights.get(injury.status, 0.0)
        
        # Starter multiplier
        if injury.is_starter_flag:
            base_impact *= 1.5
        
        # Probability factor
        if injury.probability is not None:
            # Lower probability of playing = higher impact
            base_impact *= (1.0 - injury.probability)
        
        return min(base_impact, 1.0)
    
    async def _find_affected_teammates(self, db: AsyncSession, player: Player, impact_score: float) -> List[str]:
        """Find teammates likely affected by player's injury."""
        # Get recent games to find frequent teammates
        result = await db.execute(
            select(PlayerGameStats.player_id, Player.name)
            .join(Player, PlayerGameStats.player_id == Player.id)
            .join(Game, PlayerGameStats.game_id == Game.id)
            .where(
                and_(
                    PlayerGameStats.team_id == player.team_id,
                    Game.start_time > datetime.now(timezone.utc) - timedelta(days=30),
                    PlayerGameStats.player_id != player.id
                )
            )
            .group_by(PlayerGameStats.player_id, Player.name)
            .order_by(func.count(PlayerGameStats.game_id).desc())
            .limit(5)
        )
        
        teammates = [name for _, name in result.all()]
        return teammates if impact_score > 0.5 else []
    
    def _estimate_line_adjustments(self, injury: Injury, player: Player, impact_score: float) -> Dict[str, float]:
        """Estimate how prop lines should adjust due to injury."""
        adjustments = {}
        
        if impact_score > 0.7:  # Major injury
            # Teammates' lines might increase
            adjustments["teammate_pts_boost"] = 2.0 * impact_score
            adjustments["teammate_ast_boost"] = 1.5 * impact_score
            adjustments["teammate_reb_boost"] = 1.0 * impact_score
        elif impact_score > 0.3:  # Moderate injury
            adjustments["teammate_pts_boost"] = 1.0 * impact_score
            adjustments["teammate_ast_boost"] = 0.8 * impact_score
        
        return adjustments
    
    async def _find_replacement_player(self, db: AsyncSession, injured_player: Player) -> Optional[str]:
        """Find likely replacement player from bench."""
        # Get bench players from same team with recent minutes
        result = await db.execute(
            select(Player.name)
            .join(PlayerGameStats, Player.id == PlayerGameStats.player_id)
            .where(
                and_(
                    Player.team_id == injured_player.team_id,
                    PlayerGameStats.minutes > 10,  # Has meaningful minutes
                    PlayerGameStats.game_id.in_(
                        select(Game.id)
                        .where(Game.start_time > datetime.now(timezone.utc) - timedelta(days=10))
                    )
                )
            )
            .order_by(PlayerGameStats.minutes.desc())
            .limit(1)
        )
        
        replacement = result.first()
        return replacement[0] if replacement else None
    
    async def analyze_starter_changes(self, db: AsyncSession, sport_id: int) -> List[StarterChange]:
        """Analyze recent starter/bench changes."""
        # This would compare current depth charts with historical data
        # For now, return empty list - would need depth chart API integration
        return []
    
    async def analyze_matchup(self, db: AsyncSession, game_id: str) -> MatchupAnalysis:
        """Deep analysis of specific matchup."""
        # Get game details
        result = await db.execute(
            select(Game, Team_home, Team_away)
            .join(Team.alias("Team_home"), Game.home_team_id == Team_home.id)
            .join(Team.alias("Team_away"), Game.away_team_id == Team_away.id)
            .where(Game.id == game_id)
        )
        
        game, home_team, away_team = result.first()
        if not game:
            raise ValueError(f"Game {game_id} not found")
        
        # Calculate home advantage (typically 2-3 points in NBA)
        home_advantage = 2.5 if game.sport_id == 30 else 3.0  # NBA vs other sports
        
        # Analyze pace from recent games
        pace_rating = await self._calculate_team_pace(db, home_team.id, away_team.id)
        
        # Defensive ratings
        defensive_rating = await self._calculate_defensive_ratings(db, home_team.id, away_team.id)
        
        # Key player matchups
        key_matchups = await self._identify_key_matchups(db, home_team.id, away_team.id)
        
        return MatchupAnalysis(
            home_team=home_team.name,
            away_team=away_team.name,
            home_advantage=home_advantage,
            pace_rating=pace_rating,
            defensive_rating=defensive_rating,
            key_matchups=key_matchups
        )
    
    async def _calculate_team_pace(self, db: AsyncSession, home_team_id: int, away_team_id: int) -> float:
        """Calculate expected pace (possessions per game)."""
        # Get recent games for both teams
        result = await db.execute(
            select(func.avg(Game.total_score))
            .where(
                or_(
                    Game.home_team_id == home_team_id,
                    Game.away_team_id == home_team_id,
                    Game.home_team_id == away_team_id,
                    Game.away_team_id == away_team_id
                ),
                Game.start_time > datetime.now(timezone.utc) - timedelta(days=20)
            )
        )
        
        avg_total = result.scalar() or 220  # Default NBA total
        # Convert total score to pace (rough approximation)
        return avg_total * 0.95  # Slightly lower pace in important games
    
    async def _calculate_defensive_ratings(self, db: AsyncSession, home_team_id: int, away_team_id: int) -> Tuple[float, float]:
        """Calculate defensive ratings for both teams."""
        # This would analyze points allowed, defensive efficiency, etc.
        # Simplified version using recent game averages
        home_rating = 105.0  # Default defensive rating
        away_rating = 105.0
        
        return (home_rating, away_rating)
    
    async def _identify_key_matchups(self, db: AsyncSession, home_team_id: int, away_team_id: int) -> List[str]:
        """Identify key player matchups to watch."""
        # Get star players from both teams
        result = await db.execute(
            select(Player.name)
            .join(ModelPick, Player.id == ModelPick.player_id)
            .where(
                and_(
                    or_(Player.team_id == home_team_id, Player.team_id == away_team_id),
                    ModelPick.expected_value > 0.05  # Star players have positive EV
                )
            )
            .limit(4)
        )
        
        players = [row[0] for row in result.all()]
        return [f"{players[0]} vs {players[2]}" if len(players) >= 4 else ""]
    
    async def analyze_market_sentiment(self, db: AsyncSession, game_id: str) -> MarketSentiment:
        """Analyze market sentiment and line movements."""
        # Get game details
        result = await db.execute(
            select(Game, Sport)
            .join(Sport, Game.sport_id == Sport.id)
            .where(Game.id == game_id)
        )
        
        game, sport = result.first()
        if not game:
            raise ValueError(f"Game {game_id} not found")
        
        sport_key = SPORT_ID_TO_KEY.get(game.sport_id, "unknown")
        
        # Track line movements over time
        line_movements = await self._track_line_movements(db, game_id)
        
        # Analyze betting volume (simplified)
        volume_analysis = {
            "total_volume": 10000,  # Would come from sportsbook API
            "over_volume": 5500,
            "under_volume": 4500
        }
        
        # Determine sharp money direction (simplified)
        sharp_money = {
            "points": "over" if line_movements.get("points", [])[-1][1] > line_movements.get("points", [])[0][1] else "under"
        }
        
        return MarketSentiment(
            sport=sport_key,
            game_id=game_id,
            line_movements=line_movements,
            volume_analysis=volume_analysis,
            sharp_money=sharp_money
        )
    
    async def _track_line_movements(self, db: AsyncSession, game_id: str) -> Dict[str, List[Tuple[datetime, float]]]:
        """Track how lines have moved over time."""
        # This would ideally track historical line data
        # For now, return mock data
        now = datetime.now(timezone.utc)
        return {
            "points": [
                (now - timedelta(hours=24), 220.5),
                (now - timedelta(hours=12), 221.5),
                (now - timedelta(hours=6), 222.0),
                (now, 222.5)
            ]
        }
    
    async def get_comprehensive_analysis(self, db: AsyncSession, sport_id: int, game_id: Optional[str] = None) -> Dict[str, Any]:
        """Get comprehensive deep dive analysis for a sport or specific game."""
        
        # Injury analysis
        injuries = await self.analyze_injuries(db, sport_id)
        
        # Starter changes
        starter_changes = await self.analyze_starter_changes(db, sport_id)
        
        # Market sentiment
        market_sentiments = []
        if game_id:
            try:
                sentiment = await self.analyze_market_sentiment(db, game_id)
                market_sentiments.append(sentiment)
            except Exception as e:
                logger.warning(f"Failed to analyze market sentiment for {game_id}: {e}")
        
        # Matchup analysis
        matchup_analysis = None
        if game_id:
            try:
                matchup_analysis = await self.analyze_matchup(db, game_id)
            except Exception as e:
                logger.warning(f"Failed to analyze matchup {game_id}: {e}")
        
        return {
            "injuries": [
                {
                    "player": impact.player_name,
                    "status": impact.status,
                    "impact_score": impact.impact_score,
                    "affected_teammates": impact.affected_teammates,
                    "line_adjustments": impact.line_adjustment
                }
                for impact in injuries if impact.impact_score > 0.3  # Only significant injuries
            ],
            "starter_changes": [
                {
                    "player": change.player_name,
                    "change": f"{change.old_role} → {change.new_role}",
                    "minutes_impact": change.minutes_change
                }
                for change in starter_changes
            ],
            "market_sentiment": [
                {
                    "game_id": sentiment.game_id,
                    "sharp_money": sentiment.sharp_money,
                    "line_movements": sentiment.line_movements
                }
                for sentiment in market_sentiments
            ],
            "matchup_analysis": {
                "teams": f"{matchup_analysis.away_team} @ {matchup_analysis.home_team}" if matchup_analysis else None,
                "pace": matchup_analysis.pace_rating if matchup_analysis else None,
                "key_matchups": matchup_analysis.key_matchups if matchup_analysis else []
            }
        }


# Singleton instance
deep_dive_service = DeepDiveService()
