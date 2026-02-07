"""
Sports Intelligence Brain - Real-time news, weather, and sports monitoring.

Continuously monitors:
- Sports news and updates
- Weather conditions and forecasts
- In-game events and momentum shifts
- Player sentiment and social media
- Dynamic decision making with reasoning
- Automatic code updates and git integration
"""

import asyncio
import json
import logging
import subprocess
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from collections import defaultdict, deque
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, text, func, update

from app.core.config import get_settings
from app.core.database import get_session_maker
from app.models import (
    ModelPick, Player, Game, Team, Market, Line, 
    Injury, PlayerGameStats, Sport
)
from app.services.cache_service import cache_service

logger = logging.getLogger(__name__)

@dataclass
class NewsItem:
    """Sports news item with impact analysis."""
    source: str
    title: str
    content: str
    timestamp: datetime
    players_mentioned: List[int]
    teams_mentioned: List[int]
    impact_score: float  # -1.0 to 1.0 (negative to positive)
    sentiment: str  # "positive", "negative", "neutral"
    category: str  # "injury", "trade", "suspension", "personal", "performance"
    confidence: float  # 0.0 to 1.0

@dataclass
class WeatherCondition:
    """Weather condition and impact analysis."""
    game_id: int
    venue: str
    temperature: float
    humidity: float
    wind_speed: float
    precipitation: float
    condition: str  # "clear", "rain", "snow", "windy", "extreme"
    impact_on_over_under: str  # "over_favoring", "under_favoring", "neutral"
    reasoning: str
    timestamp: datetime

@dataclass
class DecisionRecommendation:
    """AI decision recommendation with reasoning."""
    player_id: int
    player_name: str
    stat_type: str
    current_line: float
    recommendation: str  # "over", "under", "pass", "avoid"
    confidence: float
    reasoning: List[str]
    factors: Dict[str, Any]
    expected_impact: float  # -1.0 to 1.0
    timestamp: datetime

class SportsIntelligenceBrain:
    """Sports intelligence brain for real-time monitoring and decision making."""
    
    def __init__(self):
        self.settings = get_settings()
        self.is_running = False
        self.cycle_count = 0
        self.last_cycle_time = None
        self.last_git_push = None
        
        # Monitoring data structures
        self.news_items: deque = deque(maxlen=500)
        self.weather_conditions: Dict[int, WeatherCondition] = {}
        self.decision_recommendations: Dict[str, DecisionRecommendation] = {}
        self.sentiment_scores: Dict[int, float] = {}
        
        # Performance metrics
        self.news_processed = 0
        self.weather_updates = 0
        self.decisions_made = 0
        self.code_updates = 0
        self.git_pushes = 0
        self.errors = deque(maxlen=100)
        
        # Configuration
        self.monitoring_interval = 60  # seconds
        self.decision_threshold = 0.7  # confidence threshold for decisions
        
        # Git configuration
        self.git_repo_path = "c:/Users/preio/perplex-edge"
        self.auto_git_push = True
        self.min_changes_for_push = 3
        
    async def start_monitoring(self):
        """Start the sports intelligence monitoring brain."""
        if self.is_running:
            logger.warning("[INTELLIGENCE_BRAIN] Already running")
            return
            
        self.is_running = True
        logger.info("[INTELLIGENCE_BRAIN] Starting sports intelligence monitoring")
        
        try:
            while self.is_running:
                cycle_start = datetime.now(timezone.utc)
                
                try:
                    await self.monitoring_cycle()
                    self.cycle_count += 1
                    self.last_cycle_time = cycle_start
                    
                    # Log cycle metrics
                    cycle_duration = (datetime.now(timezone.utc) - cycle_start).total_seconds()
                    logger.info(
                        f"[INTELLIGENCE_BRAIN] Cycle {self.cycle_count} completed in {cycle_duration:.2f}s - "
                        f"News: {self.news_processed}, Weather: {self.weather_updates}, "
                        f"Decisions: {self.decisions_made}, Updates: {self.code_updates}"
                    )
                    
                except Exception as e:
                    logger.error(f"[INTELLIGENCE_BRAIN] Cycle {self.cycle_count} error: {e}")
                    self.errors.append({
                        "cycle": self.cycle_count,
                        "timestamp": datetime.now(timezone.utc),
                        "error": str(e)
                    })
                
                # Sleep until next cycle
                await asyncio.sleep(self.monitoring_interval)
                
        except asyncio.CancelledError:
            logger.info("[INTELLIGENCE_BRAIN] Monitoring cancelled")
        except Exception as e:
            logger.error(f"[INTELLIGENCE_BRAIN] Fatal error: {e}")
        finally:
            self.is_running = False
            logger.info("[INTELLIGENCE_BRAIN] Monitoring stopped")
    
    async def stop_monitoring(self):
        """Stop the sports intelligence monitoring brain."""
        self.is_running = False
        logger.info("[INTELLIGENCE_BRAIN] Stop signal sent")
    
    async def monitoring_cycle(self):
        """Single monitoring cycle."""
        async with get_session_maker()() as db:
            # 1. Monitor sports news and updates
            await self.monitor_sports_news(db)
            
            # 2. Monitor weather conditions
            await self.monitor_weather_conditions(db)
            
            # 3. Analyze and make decisions
            await self.make_intelligent_decisions(db)
            
            # 4. Update code based on decisions
            await self.update_code_based_on_decisions(db)
            
            # 5. Push changes to git if significant
            await self.push_changes_to_git()
            
            # 6. Cache results for fast access
            await self.cache_intelligence_results()
    
    async def monitor_sports_news(self, db: AsyncSession):
        """Monitor sports news and updates."""
        try:
            # Get active games and players
            result = await db.execute(text("""
                SELECT DISTINCT 
                    p.id as player_id, p.name as player_name,
                    t.id as team_id, t.name as team_name,
                    g.id as game_id, g.start_time
                FROM players p
                JOIN teams t ON p.team_id = t.id
                JOIN games g ON t.id IN (g.home_team_id, g.away_team_id)
                WHERE g.start_time > NOW() - INTERVAL '6 hours'
                AND g.start_time < NOW() + INTERVAL '48 hours'
                ORDER BY g.start_time
                LIMIT 100
            """))
            
            active_players = result.fetchall()
            
            # Simulate news monitoring (in production, integrate with real news APIs)
            news_items = []
            for player in active_players[:10]:  # Limit for demo
                # Simulate news items with various impacts
                news_item = NewsItem(
                    source="simulated_news",
                    title=f"Update on {player.player_name}",
                    content=f"Recent developments affecting {player.player_name}'s performance",
                    timestamp=datetime.now(timezone.utc),
                    players_mentioned=[player.player_id],
                    teams_mentioned=[player.team_id],
                    impact_score=self._simulate_impact_score(),
                    sentiment=self._simulate_sentiment(),
                    category=self._simulate_news_category(),
                    confidence=0.8
                )
                news_items.append(news_item)
            
            # Process news items
            for news_item in news_items:
                self.news_items.append(news_item)
                self.news_processed += 1
                
                # Update sentiment scores
                for player_id in news_item.players_mentioned:
                    current_sentiment = self.sentiment_scores.get(player_id, 0.0)
                    self.sentiment_scores[player_id] = (current_sentiment + news_item.impact_score) / 2
                
                # Log significant news
                if abs(news_item.impact_score) >= 0.5:
                    logger.info(
                        f"[INTELLIGENCE_BRAIN] SIGNIFICANT NEWS: {news_item.title} "
                        f"(Impact: {news_item.impact_score:.2f}, Sentiment: {news_item.sentiment})"
                    )
            
        except Exception as e:
            logger.error(f"[INTELLIGENCE_BRAIN] News monitoring error: {e}")
            raise
    
    async def monitor_weather_conditions(self, db: AsyncSession):
        """Monitor weather conditions for active games."""
        try:
            # Get today's games with venue information
            result = await db.execute(text("""
                SELECT 
                    g.id as game_id, g.start_time,
                    t.name as home_team, venue.name as venue_name,
                    venue.city, venue.state, venue.country
                FROM games g
                JOIN teams t ON g.home_team_id = t.id
                LEFT JOIN venues venue ON t.venue_id = venue.id
                WHERE g.start_time > NOW() - INTERVAL '6 hours'
                AND g.start_time < NOW() + INTERVAL '24 hours'
                ORDER BY g.start_time
                LIMIT 50
            """))
            
            games = result.fetchall()
            
            for game in games:
                # Simulate weather monitoring (in production, integrate with real weather APIs)
                weather_condition = WeatherCondition(
                    game_id=game.game_id,
                    venue=game.venue_name or f"{game.city}, {game.state}",
                    temperature=self._simulate_temperature(),
                    humidity=self._simulate_humidity(),
                    wind_speed=self._simulate_wind_speed(),
                    precipitation=self._simulate_precipitation(),
                    condition=self._simulate_weather_condition(),
                    impact_on_over_under=self._analyze_weather_impact(),
                    reasoning=self._generate_weather_reasoning(),
                    timestamp=datetime.now(timezone.utc)
                )
                
                self.weather_conditions[game.game_id] = weather_condition
                self.weather_updates += 1
                
                # Log significant weather
                if weather_condition.condition in ["rain", "snow", "extreme"]:
                    logger.info(
                        f"[INTELLIGENCE_BRAIN] WEATHER ALERT: {weather_condition.venue} - "
                        f"{weather_condition.condition} ({weather_condition.impact_on_over_under})"
                    )
            
        except Exception as e:
            logger.error(f"[INTELLIGENCE_BRAIN] Weather monitoring error: {e}")
            raise
    
    async def make_intelligent_decisions(self, db: AsyncSession):
        """Make intelligent decisions based on all monitored data."""
        try:
            # Get current model picks for active games
            result = await db.execute(text("""
                SELECT 
                    mp.id, mp.player_id, mp.game_id, mp.market_id,
                    mp.model_projection, mp.line_value, mp.side,
                    mp.expected_value, mp.confidence_score,
                    p.name as player_name, m.stat_type,
                    g.start_time, t.name as team_name
                FROM model_picks mp
                JOIN players p ON mp.player_id = p.id
                JOIN markets m ON mp.market_id = m.id
                JOIN games g ON mp.game_id = g.id
                LEFT JOIN teams t ON p.team_id = t.id
                WHERE mp.generated_at > NOW() - INTERVAL '4 hours'
                AND mp.line_value IS NOT NULL AND mp.line_value > 0
                AND g.start_time > NOW() - INTERVAL '6 hours'
                AND g.start_time < NOW() + INTERVAL '24 hours'
                ORDER BY mp.expected_value DESC
                LIMIT 50
            """))
            
            picks = result.fetchall()
            
            for pick in picks:
                # Analyze all factors for this pick
                factors = await self._analyze_pick_factors(db, pick)
                recommendation = await self._generate_recommendation(pick, factors)
                
                # Store recommendation
                rec_key = f"{pick.player_id}_{pick.market_id}"
                self.decision_recommendations[rec_key] = recommendation
                self.decisions_made += 1
                
                # Log strong recommendations
                if recommendation.confidence >= 0.8 and recommendation.recommendation != "pass":
                    logger.info(
                        f"[INTELLIGENCE_BRAIN] STRONG RECOMMENDATION: {recommendation.player_name} "
                        f"{recommendation.stat_type} {recommendation.recommendation} "
                        f"(Confidence: {recommendation.confidence:.2f}, Impact: {recommendation.expected_impact:.2f})"
                    )
            
        except Exception as e:
            logger.error(f"[INTELLIGENCE_BRAIN] Decision making error: {e}")
            raise
    
    async def _analyze_pick_factors(self, db: AsyncSession, pick) -> Dict[str, Any]:
        """Analyze all factors affecting a pick."""
        factors = {
            "news_impact": 0.0,
            "weather_impact": 0.0,
            "sentiment_score": 0.0,
            "momentum": 0.0,
            "travel_impact": 0.0,
            "schedule_impact": 0.0
        }
        
        # News impact
        recent_news = [n for n in self.news_items if pick.player_id in n.players_mentioned]
        if recent_news:
            factors["news_impact"] = sum(n.impact_score for n in recent_news[-5:]) / len(recent_news)
        
        # Weather impact
        weather = self.weather_conditions.get(pick.game_id)
        if weather:
            if weather.impact_on_over_under == "over_favoring" and pick.side == "over":
                factors["weather_impact"] = 0.3
            elif weather.impact_on_over_under == "under_favoring" and pick.side == "under":
                factors["weather_impact"] = 0.3
            elif weather.impact_on_over_under != "neutral":
                factors["weather_impact"] = -0.2
        
        # Sentiment score
        factors["sentiment_score"] = self.sentiment_scores.get(pick.player_id, 0.0)
        
        # Simulate other factors
        factors["momentum"] = self._simulate_momentum()
        factors["travel_impact"] = self._simulate_travel_impact()
        factors["schedule_impact"] = self._simulate_schedule_impact()
        
        return factors
    
    async def _generate_recommendation(self, pick, factors: Dict[str, Any]) -> DecisionRecommendation:
        """Generate intelligent recommendation with reasoning."""
        # Calculate overall impact
        overall_impact = sum(factors.values()) / len(factors)
        
        # Adjust original expected value
        original_ev = pick.expected_value or 0.0
        adjusted_ev = original_ev + (overall_impact * 0.1)  # 10% adjustment factor
        
        # Generate reasoning
        reasoning = []
        
        if abs(factors["news_impact"]) > 0.3:
            reasoning.append(f"News impact: {factors['news_impact']:.2f}")
        
        if abs(factors["weather_impact"]) > 0.2:
            reasoning.append(f"Weather conditions: {factors['weather_impact']:.2f}")
        
        if abs(factors["sentiment_score"]) > 0.4:
            reasoning.append(f"Player sentiment: {factors['sentiment_score']:.2f}")
        
        # Determine recommendation
        if adjusted_ev > 0.05 and overall_impact > 0.2:
            recommendation = "over" if pick.side == "over" else "under"
        elif adjusted_ev < -0.05 or overall_impact < -0.3:
            recommendation = "avoid"
        else:
            recommendation = "pass"
        
        # Calculate confidence
        base_confidence = pick.confidence_score or 0.5
        factor_confidence = min(abs(overall_impact), 1.0)
        confidence = (base_confidence + factor_confidence) / 2
        
        return DecisionRecommendation(
            player_id=pick.player_id,
            player_name=pick.player_name,
            stat_type=pick.stat_type,
            current_line=pick.line_value,
            recommendation=recommendation,
            confidence=confidence,
            reasoning=reasoning,
            factors=factors,
            expected_impact=overall_impact,
            timestamp=datetime.now(timezone.utc)
        )
    
    async def update_code_based_on_decisions(self, db: AsyncSession):
        """Update code based on intelligent decisions."""
        try:
            # Get strong recommendations that require code updates
            strong_recommendations = [
                rec for rec in self.decision_recommendations.values()
                if rec.confidence >= 0.8 and rec.recommendation in ["over", "under", "avoid"]
            ]
            
            if len(strong_recommendations) >= self.min_changes_for_push:
                # Update model picks with new intelligence
                updates_made = 0
                
                for rec in strong_recommendations[:10]:  # Limit updates
                    try:
                        # Update the pick with new expected value
                        new_ev = rec.expected_impact * 0.1  # Convert impact to EV adjustment
                        
                        await db.execute(text(f"""
                            UPDATE model_picks 
                            SET expected_value = expected_value + {new_ev},
                                confidence_score = GREATEST(confidence_score, {rec.confidence}),
                                updated_at = NOW()
                            WHERE player_id = {rec.player_id}
                            AND stat_type = '{rec.stat_type}'
                            AND generated_at > NOW() - INTERVAL '6 hours'
                        """))
                        
                        updates_made += 1
                        
                    except Exception as e:
                        logger.error(f"[INTELLIGENCE_BRAIN] Failed to update pick {rec.player_id}: {e}")
                
                if updates_made > 0:
                    await db.commit()
                    self.code_updates += updates_made
                    logger.info(f"[INTELLIGENCE_BRAIN] Updated {updates_made} picks with intelligence")
            
        except Exception as e:
            logger.error(f"[INTELLIGENCE_BRAIN] Code update error: {e}")
            await db.rollback()
            raise
    
    async def push_changes_to_git(self):
        """Push changes to git if significant updates were made."""
        try:
            if not self.auto_git_push:
                return
            
            # Check if enough time has passed since last push
            if self.last_git_push and (datetime.now(timezone.utc) - self.last_git_push) < timedelta(hours=1):
                return
            
            if self.code_updates >= self.min_changes_for_push:
                # Git commands
                commands = [
                    ["git", "add", "."],
                    ["git", "commit", "-m", f"🧠 INTELLIGENCE BRAIN UPDATE - Cycle {self.cycle_count}\n\n- Updated {self.code_updates} picks with AI intelligence\n- Processed {self.news_processed} news items\n- Monitored {self.weather_updates} weather conditions\n- Made {self.decisions_made} intelligent decisions\n\nAuto-generated by Sports Intelligence Brain"],
                    ["git", "push", "origin", "main"]
                ]
                
                for cmd in commands:
                    try:
                        result = subprocess.run(
                            cmd, 
                            cwd=self.git_repo_path,
                            capture_output=True, 
                            text=True, 
                            timeout=30
                        )
                        
                        if result.returncode != 0:
                            logger.error(f"[INTELLIGENCE_BRAIN] Git command failed: {cmd} - {result.stderr}")
                            return
                        
                    except subprocess.TimeoutExpired:
                        logger.error(f"[INTELLIGENCE_BRAIN] Git command timeout: {cmd}")
                        return
                    except Exception as e:
                        logger.error(f"[INTELLIGENCE_BRAIN] Git command error: {cmd} - {e}")
                        return
                
                self.git_pushes += 1
                self.last_git_push = datetime.now(timezone.utc)
                self.code_updates = 0  # Reset counter
                
                logger.info(f"[INTELLIGENCE_BRAIN] Git push #{self.git_pushes} completed successfully")
            
        except Exception as e:
            logger.error(f"[INTELLIGENCE_BRAIN] Git push error: {e}")
    
    async def cache_intelligence_results(self):
        """Cache intelligence results for fast API access."""
        try:
            # Cache news items
            recent_news = [
                {
                    "source": n.source,
                    "title": n.title,
                    "impact_score": n.impact_score,
                    "sentiment": n.sentiment,
                    "category": n.category,
                    "timestamp": n.timestamp.isoformat()
                }
                for n in list(self.news_items)[-20:]
            ]
            await cache_service.set("intelligence_news", recent_news, ttl=300)
            
            # Cache weather conditions
            weather_data = [
                {
                    "game_id": game_id,
                    "venue": weather.venue,
                    "condition": weather.condition,
                    "impact_on_over_under": weather.impact_on_over_under,
                    "timestamp": weather.timestamp.isoformat()
                }
                for game_id, weather in self.weather_conditions.items()
            ]
            await cache_service.set("intelligence_weather", weather_data, ttl=600)
            
            # Cache recommendations
            recommendations = [
                {
                    "player_id": rec.player_id,
                    "player_name": rec.player_name,
                    "stat_type": rec.stat_type,
                    "recommendation": rec.recommendation,
                    "confidence": rec.confidence,
                    "expected_impact": rec.expected_impact,
                    "reasoning": rec.reasoning,
                    "timestamp": rec.timestamp.isoformat()
                }
                for rec in list(self.decision_recommendations.values())[:15]
            ]
            await cache_service.set("intelligence_recommendations", recommendations, ttl=300)
            
        except Exception as e:
            logger.error(f"[INTELLIGENCE_BRAIN] Caching error: {e}")
    
    # Simulation methods (in production, replace with real APIs)
    def _simulate_impact_score(self) -> float:
        """Simulate news impact score."""
        import random
        return random.uniform(-1.0, 1.0)
    
    def _simulate_sentiment(self) -> str:
        """Simulate news sentiment."""
        import random
        return random.choice(["positive", "negative", "neutral"])
    
    def _simulate_news_category(self) -> str:
        """Simulate news category."""
        import random
        return random.choice(["injury", "trade", "suspension", "personal", "performance"])
    
    def _simulate_temperature(self) -> float:
        """Simulate temperature."""
        import random
        return random.uniform(20.0, 90.0)
    
    def _simulate_humidity(self) -> float:
        """Simulate humidity."""
        import random
        return random.uniform(30.0, 90.0)
    
    def _simulate_wind_speed(self) -> float:
        """Simulate wind speed."""
        import random
        return random.uniform(0.0, 25.0)
    
    def _simulate_precipitation(self) -> float:
        """Simulate precipitation."""
        import random
        return random.uniform(0.0, 2.0)
    
    def _simulate_weather_condition(self) -> str:
        """Simulate weather condition."""
        import random
        return random.choice(["clear", "rain", "snow", "windy", "extreme"])
    
    def _analyze_weather_impact(self) -> str:
        """Analyze weather impact on over/under."""
        import random
        return random.choice(["over_favoring", "under_favoring", "neutral"])
    
    def _generate_weather_reasoning(self) -> str:
        """Generate weather reasoning."""
        return "Weather conditions affect scoring pace and player performance"
    
    def _simulate_momentum(self) -> float:
        """Simulate team momentum."""
        import random
        return random.uniform(-1.0, 1.0)
    
    def _simulate_travel_impact(self) -> float:
        """Simulate travel fatigue impact."""
        import random
        return random.uniform(-0.5, 0.5)
    
    def _simulate_schedule_impact(self) -> float:
        """Simulate schedule density impact."""
        import random
        return random.uniform(-0.3, 0.3)
    
    def get_status(self) -> Dict[str, Any]:
        """Get current brain status."""
        return {
            "is_running": self.is_running,
            "cycle_count": self.cycle_count,
            "last_cycle_time": self.last_cycle_time.isoformat() if self.last_cycle_time else None,
            "monitoring_interval": self.monitoring_interval,
            "metrics": {
                "news_processed": self.news_processed,
                "weather_updates": self.weather_updates,
                "decisions_made": self.decisions_made,
                "code_updates": self.code_updates,
                "git_pushes": self.git_pushes
            },
            "tracking": {
                "news_items": len(self.news_items),
                "weather_conditions": len(self.weather_conditions),
                "decision_recommendations": len(self.decision_recommendations),
                "sentiment_scores": len(self.sentiment_scores)
            },
            "git_status": {
                "auto_push_enabled": self.auto_git_push,
                "last_push": self.last_git_push.isoformat() if self.last_git_push else None,
                "min_changes_for_push": self.min_changes_for_push
            },
            "recent_errors": list(self.errors)[-5:] if self.errors else []
        }

# Global sports intelligence brain instance
sports_intelligence_brain = SportsIntelligenceBrain()
