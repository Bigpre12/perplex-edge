"""
Multi-Book Shopper - Find best odds across sportsbooks
"""

from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
from sqlalchemy.orm import selectinload

from app.models import ModelPick, Game, Player, Market

@dataclass
class BookOdds:
    """Odds from a specific sportsbook."""
    book_name: str
    odds: float
    american_odds: int
    implied_probability: float
    limit: int
    available: bool

@dataclass
class BestOddsResult:
    """Best odds result for a pick."""
    pick_id: int
    player_name: str
    stat_type: str
    line_value: float
    side: str
    best_book: str
    best_odds: float
    best_american_odds: int
    best_implied_prob: float
    all_books: List[BookOdds]
    ev_improvement: float
    arbitrage_opportunity: bool

class MultiBookShopper:
    """Finds best odds across multiple sportsbooks and identifies arbitrage opportunities."""
    
    def __init__(self):
        self.supported_books = [
            "DraftKings", "FanDuel", "BetMGM", "Caesars", "PointsBet",
            "WynnBET", "BetRivers", "Unibet", "Barstool", "FOX Bet"
        ]
        self.arbitrage_threshold = 0.02  # 2% threshold for arbitrage
        
    def decimal_to_american(self, decimal_odds: float) -> int:
        """Convert decimal odds to American odds."""
        if decimal_odds >= 2.0:
            return int((decimal_odds - 1) * 100)
        else:
            return int(-100 / (decimal_odds - 1))
    
    def american_to_decimal(self, american_odds: int) -> float:
        """Convert American odds to decimal odds."""
        if american_odds > 0:
            return (american_odds / 100) + 1
        else:
            return (100 / abs(american_odds)) + 1
    
    def american_to_implied_prob(self, american_odds: int) -> float:
        """Convert American odds to implied probability."""
        if american_odds > 0:
            return 100 / (american_odds + 100)
        else:
            return abs(american_odds) / (abs(american_odds) + 100)
    
    def calculate_ev_improvement(
        self,
        original_odds: int,
        best_odds: int,
        model_prob: float
    ) -> float:
        """Calculate EV improvement from better odds."""
        
        # Original EV
        if original_odds < 0:
            original_profit = 100 / abs(original_odds)
        else:
            original_profit = original_odds / 100
        
        original_ev = (model_prob * original_profit) - ((1 - model_prob) * 1)
        
        # Best EV
        if best_odds < 0:
            best_profit = 100 / abs(best_odds)
        else:
            best_profit = best_odds / 100
        
        best_ev = (model_prob * best_profit) - ((1 - model_prob) * 1)
        
        return best_ev - original_ev
    
    def detect_arbitrage_opportunity(
        self,
        book_odds: List[BookOdds]
    ) -> Optional[Dict[str, Any]]:
        """
        Detect arbitrage opportunity across books.
        
        Args:
            book_odds: List of odds from different books
        
        Returns:
            Arbitrage opportunity data or None
        """
        
        if len(book_odds) < 2:
            return None
        
        # Find highest and lowest odds
        highest_odds = max(book_odds, key=lambda x: x.odds)
        lowest_odds = min(book_odds, key=lambda x: x.odds)
        
        # Calculate arbitrage profit
        if highest_odds.book_name != lowest_odds.book_name:
            # Simple arbitrage calculation
            total_implied_prob = highest_odds.implied_probability + (1 - lowest_odds.implied_probability)
            
            if total_implied_prob < 0.98:  # 2% margin for arbitrage
                arbitrage_profit = (1 / total_implied_prob) - 1
                
                return {
                    "type": "sure_bet",
                    "highest_odds": {
                        "book": highest_odds.book_name,
                        "odds": highest_odds.american_odds,
                        "side": "over" if highest_odds.book_name == book_odds[0].book_name else "under"
                    },
                    "lowest_odds": {
                        "book": lowest_odds.book_name,
                        "odds": lowest_odds.american_odds,
                        "side": "under" if lowest_odds.book_name == book_odds[0].book_name else "over"
                    },
                    "total_implied_probability": total_implied_prob,
                    "arbitrage_profit": arbitrage_profit,
                    "profit_percentage": arbitrage_profit * 100
                }
        
        return None
    
    async def get_multi_book_odds(
        self,
        db: AsyncSession,
        player_id: int,
        market_id: int,
        line_value: float,
        side: str
    ) -> List[BookOdds]:
        """
        Get odds from multiple sportsbooks for a specific pick.
        
        Args:
            db: Database session
            player_id: Player ID
            market_id: Market ID
            line_value: Line value
            side: Over/under
        
        Returns:
            List of BookOdds from different sportsbooks
        """
        
        # Mock multi-book data - in production, this would query actual sportsbook APIs
        book_odds = []
        
        # Generate mock odds for different books
        base_odds = -110  # Base odds
        
        for book in self.supported_books:
            # Add some variation to odds
            import random
            odds_variation = random.uniform(-5, 5)
            book_odds = base_odds + odds_variation
            
            # Generate limit (higher for popular books)
            if book in ["DraftKings", "FanDuel"]:
                limit = random.randint(5000, 20000)
            elif book in ["BetMGM", "Caesars"]:
                limit = random.randint(2000, 10000)
            else:
                limit = random.randint(1000, 5000)
            
            # Check availability (mock)
            available = random.random() > 0.1  # 90% availability
            
            if available:
                book_odds.append(BookOdds(
                    book_name=book,
                    odds=book_odds,
                    american_odds=int(book_odds),
                    implied_probability=self.american_to_implied_prob(int(book_odds)),
                    limit=limit,
                    available=True
                ))
        
        return book_odds
    
    async def find_best_odds_for_pick(
        self,
        db: AsyncSession,
        pick_id: int,
        model_prob: float
    ) -> BestOddsResult:
        """
        Find best odds across all sportsbooks for a specific pick.
        
        Args:
            db: Database session
            pick_id: Pick ID
            model_prob: Model probability for this pick
        
        Returns:
            BestOddsResult with best odds and arbitrage info
        """
        
        # Get pick details
        query = select(ModelPick).options(
            selectinload(ModelPick.player),
            selectinload(ModelPick.market)
        ).where(ModelPick.id == pick_id)
        
        result = await db.execute(query)
        pick = result.scalar_one_or_none()
        
        if not pick:
            raise ValueError(f"Pick {pick_id} not found")
        
        # Get multi-book odds
        book_odds = await self.get_multi_book_odds(
            db, pick.player_id, pick.market_id, pick.line_value, pick.side
        )
        
        if not book_odds:
            raise ValueError("No odds available from any sportsbook")
        
        # Find best odds
        best_odds_data = max(book_odds, key=lambda x: x.odds)
        
        # Calculate EV improvement
        ev_improvement = self.calculate_ev_improvement(
            pick.odds, best_odds_data.american_odds, model_prob
        )
        
        # Check for arbitrage
        arbitrage = self.detect_arbitrage_opportunity(book_odds)
        
        return BestOddsResult(
            pick_id=pick_id,
            player_name=pick.player.name if pick.player else "Unknown",
            stat_type=pick.market.stat_type if pick.market else "Unknown",
            line_value=pick.line_value,
            side=pick.side,
            best_book=best_odds_data.book_name,
            best_odds=best_odds_data.odds,
            best_american_odds=best_odds_data.american_odds,
            best_implied_prob=best_odds_data.implied_probability,
            all_books=book_odds,
            ev_improvement=ev_improvement,
            arbitrage_opportunity=arbitrage is not None
        )
    
    async def find_best_odds_for_game(
        self,
        db: AsyncSession,
        game_id: int
    ) -> Dict[str, Any]:
        """
        Find best odds for all picks in a game.
        
        Args:
            db: Database session
            game_id: Game ID
        
        Returns:
            Dictionary with best odds for all picks
        """
        
        # Get all picks for this game
        query = select(ModelPick).options(
            selectinload(ModelPick.player),
            selectinload(ModelPick.market)
        ).where(ModelPick.game_id == game_id)
        
        result = await db.execute(query)
        picks = result.scalars().all()
        
        best_odds_results = []
        arbitrage_opportunities = []
        
        for pick in picks:
            try:
                # Mock model probability - in production, this would come from the pick
                model_prob = 0.55  # Default 55%
                
                best_odds_result = await self.find_best_odds_for_pick(
                    db, pick.id, model_prob
                )
                
                best_odds_results.append(best_odds_result)
                
                # Check for arbitrage
                if best_odds_result.arbitrage_opportunity:
                    arbitrage_opportunities.append(best_odds_result)
                    
            except Exception as e:
                print(f"Error processing pick {pick.id}: {e}")
                continue
        
        return {
            "game_id": game_id,
            "total_picks": len(picks),
            "best_odds_results": best_odds_results,
            "arbitrage_opportunities": arbitrage_opportunities,
            "summary": {
                "total_arbitrage_opportunities": len(arbitrage_opportunities),
                "avg_ev_improvement": sum(r.ev_improvement for r in best_odds_results) / len(best_odds_results) if best_odds_results else 0,
                "books_compared": len(self.supported_books)
            },
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
    
    async def get_line_shopping_summary(
        self,
        db: AsyncSession,
        sport_id: int = 30,
        hours_back: int = 24
    ) -> Dict[str, Any]:
        """
        Get line shopping summary for recent picks.
        
        Args:
            db: Database session
            sport_id: Sport ID
            hours_back: Hours to look back
        
        Returns:
            Line shopping summary
        """
        
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
        ).order_by(desc(ModelPick.generated_at))
        
        result = await db.execute(query)
        picks = result.scalars().all()
        
        best_odds_results = []
        arbitrage_opportunities = []
        book_comparison = {}
        
        for pick in picks[:50]:  # Limit to 50 picks for performance
            try:
                model_prob = 0.55  # Mock model probability
                
                best_odds_result = await self.find_best_odds_for_pick(
                    db, pick.id, model_prob
                )
                
                best_odds_results.append(best_odds_result)
                
                # Track book availability
                for book_odds in best_odds_result.all_books:
                    if book_odds.book_name not in book_comparison:
                        book_comparison[book_odds.book_name] = {
                            "available_picks": 0,
                            "best_odds_count": 0,
                            "avg_limit": 0
                        }
                    
                    book_comparison[book_odds.book_name]["available_picks"] += 1
                    book_comparison[book_odds.book_name]["avg_limit"] += book_odds.limit
                    
                    if book_odds.book_name == best_odds_result.best_book:
                        book_comparison[book_odds.book_name]["best_odds_count"] += 1
                
                if best_odds_result.arbitrage_opportunity:
                    arbitrage_opportunities.append(best_odds_result)
                    
            except Exception as e:
                print(f"Error processing pick {pick.id}: {e}")
                continue
        
        # Calculate averages
        for book in book_comparison:
            if book_comparison[book]["available_picks"] > 0:
                book_comparison[book]["avg_limit"] /= book_comparison[book]["available_picks"]
        
        return {
            "sport_id": sport_id,
            "analysis_period_hours": hours_back,
            "total_picks_analyzed": len(picks),
            "best_odds_results": best_odds_results,
            "arbitrage_opportunities": arbitrage_opportunities,
            "book_comparison": book_comparison,
            "summary": {
                "total_arbitrage_opportunities": len(arbitrage_opportunities),
                "avg_ev_improvement": sum(r.ev_improvement for r in best_odds_results) / len(best_odds_results) if best_odds_results else 0,
                "books_with_best_odds": len(set(r.best_book for r in best_odds_results)),
                "most_competitive_book": max(book_comparison.items(), key=lambda x: x[1]["best_odds_count"])[0] if book_comparison else None
            },
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
