"""Results tracker service for settling picks and calculating hit rate metrics."""

import logging
from datetime import datetime, timezone, timedelta
from typing import Any, Optional

from sqlalchemy import select, func, and_, or_, Integer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import (
    Game, ModelPick, Player, PlayerGameStats, Market, Line,
    PickResult, PlayerHitRate, Sport
)
from app.services.calibration_service import calculate_clv, calculate_profit_loss

logger = logging.getLogger(__name__)


# =============================================================================
# Stat Type Mappings
# =============================================================================

# Map market stat types to PlayerGameStats stat types
STAT_TYPE_MAP = {
    "PTS": ["PTS"],
    "REB": ["REB"],
    "AST": ["AST"],
    "3PM": ["3PM"],
    "STL": ["STL"],
    "BLK": ["BLK"],
    "TO": ["TO"],
    "PRA": ["PTS", "REB", "AST"],  # Points + Rebounds + Assists
    "PR": ["PTS", "REB"],  # Points + Rebounds
    "PA": ["PTS", "AST"],  # Points + Assists
    "RA": ["REB", "AST"],  # Rebounds + Assists
}


# =============================================================================
# Results Tracker Service
# =============================================================================

class ResultsTracker:
    """
    Service for tracking pick results and calculating hit rate metrics.
    
    This service:
    - Settles picks after games complete by comparing actual stats to lines
    - Updates player hit rate aggregates
    - Provides queries for hot players and streaks
    """
    
    def __init__(self, use_stubs: bool = False):
        self.use_stubs = use_stubs
    
    # =========================================================================
    # Pick Settlement
    # =========================================================================
    
    async def settle_picks_for_game(
        self,
        db: AsyncSession,
        game_id: int,
    ) -> dict[str, Any]:
        """
        Settle all picks for a completed game.
        
        Fetches actual player stats and compares against each pick's line
        to determine if the pick hit or missed.
        
        Args:
            db: Database session
            game_id: ID of the game to settle
        
        Returns:
            Dictionary with settlement counts
        """
        # Get the game
        game = await db.get(Game, game_id)
        if not game:
            return {"error": f"Game {game_id} not found"}
        
        # Get all active picks for this game that haven't been settled
        result = await db.execute(
            select(ModelPick)
            .outerjoin(PickResult, ModelPick.id == PickResult.pick_id)
            .where(
                and_(
                    ModelPick.game_id == game_id,
                    ModelPick.is_active == True,
                    ModelPick.player_id.isnot(None),  # Only player props for now
                    PickResult.id.is_(None),  # Not yet settled
                )
            )
            .options(selectinload(ModelPick.market))
        )
        picks = result.scalars().all()
        
        if not picks:
            return {
                "game_id": game_id,
                "message": "No unsettled picks found",
                "settled": 0,
                "hits": 0,
                "misses": 0,
            }
        
        # Get all player stats for this game
        stats_result = await db.execute(
            select(PlayerGameStats)
            .where(PlayerGameStats.game_id == game_id)
        )
        all_stats = stats_result.scalars().all()
        
        # Group stats by player_id and stat_type
        stats_map: dict[int, dict[str, float]] = {}
        for stat in all_stats:
            if stat.player_id not in stats_map:
                stats_map[stat.player_id] = {}
            stats_map[stat.player_id][stat.stat_type] = stat.value
        
        # Get closing lines for this game (most recent lines before game start)
        # These represent the "closing" odds/lines at game time
        # Join with Market to get stat_type
        closing_lines_result = await db.execute(
            select(Line, Market)
            .join(Market, Line.market_id == Market.id)
            .where(Line.game_id == game_id)
            .order_by(Line.fetched_at.desc())
        )
        closing_lines = closing_lines_result.all()
        
        # Build a map of (player_id, stat_type) -> (closing_odds, closing_line_value)
        closing_map: dict[tuple[int, str], tuple[int, float]] = {}
        for line, market in closing_lines:
            if line.player_id and market.stat_type:
                key = (line.player_id, market.stat_type.upper())
                if key not in closing_map:  # Keep only the most recent (first in desc order)
                    # Use odds as the closing odds
                    closing_map[key] = (int(line.odds), line.line_value)
        
        # Settle each pick
        settled = 0
        hits = 0
        misses = 0
        players_to_update = set()
        
        for pick in picks:
            if not pick.player_id:
                continue
            
            player_stats = stats_map.get(pick.player_id, {})
            if not player_stats:
                logger.warning(f"No stats found for player {pick.player_id} in game {game_id}")
                continue
            
            # Get the stat type from the market
            stat_type = pick.market.stat_type if pick.market else None
            if not stat_type:
                continue
            
            # Calculate actual value (may be a combination of stats)
            actual_value = self._calculate_actual_value(stat_type, player_stats)
            if actual_value is None:
                logger.warning(f"Could not calculate {stat_type} for player {pick.player_id}")
                continue
            
            # Determine if hit
            line_value = pick.line_value or 0
            side = pick.side.lower()
            
            if side == "over":
                hit = actual_value > line_value
            elif side == "under":
                hit = actual_value < line_value
            else:
                # For exact matches or other sides, skip
                continue
            
            # Get closing line data for CLV calculation
            closing_key = (pick.player_id, stat_type.upper())
            closing_data = closing_map.get(closing_key)
            
            closing_odds = None
            closing_line_val = None
            clv_cents = None
            profit_loss = None
            
            if closing_data:
                closing_odds_raw, closing_line_val = closing_data
                
                # Get the appropriate closing odds based on side
                if side == "over":
                    closing_odds = closing_odds_raw  # over_odds
                else:
                    # For under, we'd ideally have under_odds but use over_odds as approximation
                    closing_odds = closing_odds_raw
                
                # Calculate CLV if we have both opening and closing odds
                opening_odds = int(pick.odds) if pick.odds else None
                if opening_odds and closing_odds:
                    clv_cents = calculate_clv(opening_odds, closing_odds)
            
            # Calculate profit/loss
            opening_odds = int(pick.odds) if pick.odds else -110
            profit_loss = calculate_profit_loss(opening_odds, hit, unit=100.0)
            
            # Create the result record
            pick_result = PickResult(
                pick_id=pick.id,
                player_id=pick.player_id,
                game_id=game_id,
                actual_value=actual_value,
                line_value=line_value,
                side=side,
                hit=hit,
                closing_odds=closing_odds,
                closing_line=closing_line_val,
                clv_cents=clv_cents,
                profit_loss=profit_loss,
            )
            db.add(pick_result)
            
            settled += 1
            if hit:
                hits += 1
            else:
                misses += 1
            
            players_to_update.add(pick.player_id)
        
        await db.commit()
        
        # Update hit rates for affected players
        for player_id in players_to_update:
            await self.update_player_hit_rates(db, player_id)
        
        return {
            "game_id": game_id,
            "settled": settled,
            "hits": hits,
            "misses": misses,
            "hit_rate": hits / settled if settled > 0 else 0,
        }
    
    def _calculate_actual_value(
        self,
        stat_type: str,
        player_stats: dict[str, float],
    ) -> Optional[float]:
        """Calculate the actual value for a stat type from player stats."""
        stat_types = STAT_TYPE_MAP.get(stat_type.upper(), [stat_type.upper()])
        
        total = 0
        for st in stat_types:
            value = player_stats.get(st)
            if value is None:
                # If any component is missing, return None
                return None
            total += value
        
        return total
    
    # =========================================================================
    # Hit Rate Updates
    # =========================================================================
    
    async def update_player_hit_rates(
        self,
        db: AsyncSession,
        player_id: int,
    ) -> Optional[PlayerHitRate]:
        """
        Recalculate and update hit rate stats for a player.
        
        Args:
            db: Database session
            player_id: ID of the player to update
        
        Returns:
            Updated PlayerHitRate record
        """
        # Get player's sport
        player = await db.get(Player, player_id)
        if not player:
            return None
        
        # Get or create hit rate record
        result = await db.execute(
            select(PlayerHitRate).where(PlayerHitRate.player_id == player_id)
        )
        hit_rate = result.scalar_one_or_none()
        
        if not hit_rate:
            hit_rate = PlayerHitRate(
                player_id=player_id,
                sport_id=player.sport_id,
            )
            db.add(hit_rate)
        
        # Calculate 7-day stats
        seven_days_ago = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=7)
        
        result_7d = await db.execute(
            select(
                func.count(PickResult.id).label("total"),
                func.sum(func.cast(PickResult.hit, Integer)).label("hits"),
            )
            .where(
                and_(
                    PickResult.player_id == player_id,
                    PickResult.settled_at >= seven_days_ago,
                )
            )
        )
        row_7d = result_7d.one()
        hit_rate.total_7d = row_7d.total or 0
        hit_rate.hits_7d = row_7d.hits or 0
        hit_rate.hit_rate_7d = (hit_rate.hits_7d / hit_rate.total_7d) if hit_rate.total_7d > 0 else None
        
        # Calculate all-time stats
        result_all = await db.execute(
            select(
                func.count(PickResult.id).label("total"),
                func.sum(func.cast(PickResult.hit, Integer)).label("hits"),
            )
            .where(PickResult.player_id == player_id)
        )
        row_all = result_all.one()
        hit_rate.total_all = row_all.total or 0
        hit_rate.hits_all = row_all.hits or 0
        hit_rate.hit_rate_all = (hit_rate.hits_all / hit_rate.total_all) if hit_rate.total_all > 0 else None
        
        # Get recent results for streak calculation
        result_recent = await db.execute(
            select(PickResult.hit, PickResult.settled_at)
            .where(PickResult.player_id == player_id)
            .order_by(PickResult.settled_at.desc())
            .limit(20)
        )
        recent = result_recent.all()
        
        if recent:
            # Calculate current streak
            hit_rate.current_streak = self._calculate_streak([r.hit for r in recent])
            
            # Update last 5 results
            last_5 = "".join("W" if r.hit else "L" for r in recent[:5])
            hit_rate.last_5_results = last_5
            
            # Update best/worst streaks
            all_results = [r.hit for r in recent]
            best, worst = self._calculate_best_worst_streaks(all_results)
            # Handle None values from database
            current_best = hit_rate.best_streak if hit_rate.best_streak is not None else 0
            current_worst = hit_rate.worst_streak if hit_rate.worst_streak is not None else 0
            hit_rate.best_streak = max(current_best, best)
            hit_rate.worst_streak = min(current_worst, worst)
            
            hit_rate.last_pick_at = recent[0].settled_at
        
        await db.commit()
        return hit_rate
    
    def _calculate_streak(self, results: list[bool]) -> int:
        """Calculate current streak from results (most recent first)."""
        if not results:
            return 0
        
        streak = 0
        first = results[0]
        
        for r in results:
            if r == first:
                streak += 1 if first else -1
            else:
                break
        
        return streak
    
    def _calculate_best_worst_streaks(self, results: list[bool]) -> tuple[int, int]:
        """Calculate best and worst streaks from all results."""
        if not results:
            return 0, 0
        
        best = 0
        worst = 0
        current_win = 0
        current_loss = 0
        
        for r in results:
            if r:
                current_win += 1
                current_loss = 0
                best = max(best, current_win)
            else:
                current_loss += 1
                current_win = 0
                worst = min(worst, -current_loss)
        
        return best, worst
    
    # =========================================================================
    # Query Methods
    # =========================================================================
    
    async def get_hot_players(
        self,
        db: AsyncSession,
        sport_id: int,
        min_picks: int = 5,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """
        Get players with the best 7-day hit rates.
        
        Args:
            db: Database session
            sport_id: Sport to filter by
            min_picks: Minimum picks in last 7 days
            limit: Maximum players to return
        
        Returns:
            List of hot player dictionaries
        """
        result = await db.execute(
            select(PlayerHitRate, Player)
            .join(Player, PlayerHitRate.player_id == Player.id)
            .where(
                and_(
                    PlayerHitRate.sport_id == sport_id,
                    PlayerHitRate.total_7d >= min_picks,
                    PlayerHitRate.hit_rate_7d.isnot(None),
                )
            )
            .order_by(PlayerHitRate.hit_rate_7d.desc())
            .limit(limit)
        )
        
        hot_players = []
        for hit_rate, player in result.all():
            hot_players.append({
                "player_id": player.id,
                "player_name": player.name,
                "hit_rate_7d": hit_rate.hit_rate_7d,
                "total_7d": hit_rate.total_7d,
                "hits_7d": hit_rate.hits_7d,
                "current_streak": hit_rate.current_streak,
                "last_5": hit_rate.last_5_results,
            })
        
        return hot_players
    
    async def get_cold_players(
        self,
        db: AsyncSession,
        sport_id: int,
        min_picks: int = 5,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """
        Get players with the worst 7-day hit rates.
        
        Args:
            db: Database session
            sport_id: Sport to filter by
            min_picks: Minimum picks in last 7 days
            limit: Maximum players to return
        
        Returns:
            List of cold player dictionaries
        """
        result = await db.execute(
            select(PlayerHitRate, Player)
            .join(Player, PlayerHitRate.player_id == Player.id)
            .where(
                and_(
                    PlayerHitRate.sport_id == sport_id,
                    PlayerHitRate.total_7d >= min_picks,
                    PlayerHitRate.hit_rate_7d.isnot(None),
                )
            )
            .order_by(PlayerHitRate.hit_rate_7d.asc())
            .limit(limit)
        )
        
        cold_players = []
        for hit_rate, player in result.all():
            cold_players.append({
                "player_id": player.id,
                "player_name": player.name,
                "hit_rate_7d": hit_rate.hit_rate_7d,
                "total_7d": hit_rate.total_7d,
                "hits_7d": hit_rate.hits_7d,
                "current_streak": hit_rate.current_streak,
                "last_5": hit_rate.last_5_results,
            })
        
        return cold_players
    
    async def get_streaks(
        self,
        db: AsyncSession,
        sport_id: int,
        min_streak: int = 3,
        limit: int = 20,
    ) -> dict[str, list[dict[str, Any]]]:
        """
        Get players on hot and cold streaks.
        
        Args:
            db: Database session
            sport_id: Sport to filter by
            min_streak: Minimum streak length (absolute value)
            limit: Maximum players per category
        
        Returns:
            Dict with 'hot' and 'cold' player lists
        """
        # Hot streaks (positive)
        hot_result = await db.execute(
            select(PlayerHitRate, Player)
            .join(Player, PlayerHitRate.player_id == Player.id)
            .where(
                and_(
                    PlayerHitRate.sport_id == sport_id,
                    PlayerHitRate.current_streak >= min_streak,
                )
            )
            .order_by(PlayerHitRate.current_streak.desc())
            .limit(limit)
        )
        
        hot_streaks = []
        for hit_rate, player in hot_result.all():
            hot_streaks.append({
                "player_id": player.id,
                "player_name": player.name,
                "streak": hit_rate.current_streak,
                "hit_rate_7d": hit_rate.hit_rate_7d,
                "last_5": hit_rate.last_5_results,
            })
        
        # Cold streaks (negative)
        cold_result = await db.execute(
            select(PlayerHitRate, Player)
            .join(Player, PlayerHitRate.player_id == Player.id)
            .where(
                and_(
                    PlayerHitRate.sport_id == sport_id,
                    PlayerHitRate.current_streak <= -min_streak,
                )
            )
            .order_by(PlayerHitRate.current_streak.asc())
            .limit(limit)
        )
        
        cold_streaks = []
        for hit_rate, player in cold_result.all():
            cold_streaks.append({
                "player_id": player.id,
                "player_name": player.name,
                "streak": hit_rate.current_streak,
                "hit_rate_7d": hit_rate.hit_rate_7d,
                "last_5": hit_rate.last_5_results,
            })
        
        return {
            "hot": hot_streaks,
            "cold": cold_streaks,
        }
    
    async def get_recent_results(
        self,
        db: AsyncSession,
        sport_id: int,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """
        Get the most recent pick results.
        
        Args:
            db: Database session
            sport_id: Sport to filter by
            limit: Maximum results to return
        
        Returns:
            List of recent result dictionaries
        """
        result = await db.execute(
            select(PickResult, ModelPick, Player, Market, Game)
            .join(ModelPick, PickResult.pick_id == ModelPick.id)
            .join(Player, PickResult.player_id == Player.id)
            .join(Market, ModelPick.market_id == Market.id)
            .join(Game, PickResult.game_id == Game.id)
            .where(ModelPick.sport_id == sport_id)
            .order_by(PickResult.settled_at.desc())
            .limit(limit)
        )
        
        results = []
        for pick_result, pick, player, market, game in result.all():
            results.append({
                "result_id": pick_result.id,
                "player_id": player.id,
                "player_name": player.name,
                "stat_type": market.stat_type,
                "line": pick_result.line_value,
                "side": pick_result.side,
                "actual_value": pick_result.actual_value,
                "hit": pick_result.hit,
                "settled_at": pick_result.settled_at.isoformat() + "Z",
                "game_id": game.id,
            })
        
        return results
    
    async def get_player_history(
        self,
        db: AsyncSession,
        player_id: int,
        limit: int = 50,
    ) -> dict[str, Any]:
        """
        Get detailed pick history for a player.
        
        Args:
            db: Database session
            player_id: Player ID
            limit: Maximum results
        
        Returns:
            Player history dictionary
        """
        # Get player info
        player = await db.get(Player, player_id)
        if not player:
            return {"error": f"Player {player_id} not found"}
        
        # Get hit rate stats
        hit_rate_result = await db.execute(
            select(PlayerHitRate).where(PlayerHitRate.player_id == player_id)
        )
        hit_rate = hit_rate_result.scalar_one_or_none()
        
        # Get recent results
        results_query = await db.execute(
            select(PickResult, ModelPick, Market)
            .join(ModelPick, PickResult.pick_id == ModelPick.id)
            .join(Market, ModelPick.market_id == Market.id)
            .where(PickResult.player_id == player_id)
            .order_by(PickResult.settled_at.desc())
            .limit(limit)
        )
        
        results = []
        for pick_result, pick, market in results_query.all():
            results.append({
                "stat_type": market.stat_type,
                "line": pick_result.line_value,
                "side": pick_result.side,
                "actual_value": pick_result.actual_value,
                "hit": pick_result.hit,
                "settled_at": pick_result.settled_at.isoformat() + "Z",
            })
        
        return {
            "player_id": player.id,
            "player_name": player.name,
            "stats": {
                "hit_rate_7d": hit_rate.hit_rate_7d if hit_rate else None,
                "total_7d": hit_rate.total_7d if hit_rate else 0,
                "hit_rate_all": hit_rate.hit_rate_all if hit_rate else None,
                "total_all": hit_rate.total_all if hit_rate else 0,
                "current_streak": hit_rate.current_streak if hit_rate else 0,
                "best_streak": hit_rate.best_streak if hit_rate else 0,
                "worst_streak": hit_rate.worst_streak if hit_rate else 0,
                "last_5": hit_rate.last_5_results if hit_rate else None,
            },
            "results": results,
        }
    
    # =========================================================================
    # Stub Methods for Testing
    # =========================================================================
    
    async def simulate_game_results(
        self,
        db: AsyncSession,
        game_id: int,
    ) -> dict[str, Any]:
        """
        Simulate game results for testing purposes.
        
        Creates fake PlayerGameStats for all players with picks in the game,
        then settles the picks.
        
        Args:
            db: Database session
            game_id: Game to simulate
        
        Returns:
            Settlement results
        """
        import random
        
        # Verify game exists
        game = await db.get(Game, game_id)
        if not game:
            return {"error": f"Game {game_id} not found"}
        
        # Get all picks for this game
        result = await db.execute(
            select(ModelPick)
            .where(
                and_(
                    ModelPick.game_id == game_id,
                    ModelPick.player_id.isnot(None),
                    ModelPick.is_active == True,
                )
            )
            .options(selectinload(ModelPick.market))
        )
        picks = result.scalars().all()
        
        if not picks:
            return {
                "game_id": game_id,
                "message": "No player picks found for this game",
                "settled": 0,
                "hits": 0,
                "misses": 0,
                "hit_rate": 0,
            }
        
        logger.info(f"Simulating results for game {game_id} with {len(picks)} picks")
        
        # Generate simulated stats for each player
        player_lines: dict[int, list[tuple[str, float, str]]] = {}
        for pick in picks:
            if not pick.player_id:
                continue
            if pick.player_id not in player_lines:
                player_lines[pick.player_id] = []
            stat_type = pick.market.stat_type if pick.market else "PTS"
            line_value = pick.line_value if pick.line_value is not None else 0
            side = pick.side if pick.side else "over"
            player_lines[pick.player_id].append((stat_type, line_value, side))
        
        # Create simulated stats
        stats_created = 0
        for player_id, lines in player_lines.items():
            for stat_type, line_value, side in lines:
                # Simulate actual value around the line with some variance
                # Use a safe variance calculation (min 1.0 to avoid issues with 0 lines)
                variance = max(1.0, abs(line_value) * 0.2)
                
                # Slightly favor hitting the pick (55% hit rate)
                if side.lower() == "over":
                    # More likely to go over
                    actual = line_value + random.gauss(0.5, variance)
                else:
                    # More likely to go under
                    actual = line_value + random.gauss(-0.5, variance)
                
                actual = max(0, actual)  # No negative stats
                
                # Check if stat already exists
                existing = await db.execute(
                    select(PlayerGameStats).where(
                        and_(
                            PlayerGameStats.player_id == player_id,
                            PlayerGameStats.game_id == game_id,
                            PlayerGameStats.stat_type == stat_type,
                        )
                    )
                )
                if not existing.scalar_one_or_none():
                    stat = PlayerGameStats(
                        player_id=player_id,
                        game_id=game_id,
                        stat_type=stat_type,
                        value=round(actual, 1),
                        minutes=random.randint(20, 38),
                    )
                    db.add(stat)
                    stats_created += 1
        
        await db.commit()
        logger.info(f"Created {stats_created} simulated stats for game {game_id}")
        
        # Now settle the picks
        return await self.settle_picks_for_game(db, game_id)
