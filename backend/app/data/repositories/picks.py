"""
Pick Repository - Database operations for model picks.
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import List, Optional

from sqlalchemy import select, and_, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.model_pick import ModelPick
from app.data.repositories.base import BaseRepository

logger = logging.getLogger(__name__)


class PickRepository(BaseRepository[ModelPick]):
    """Repository for ModelPick database operations."""
    
    model = ModelPick
    
    async def get_active_picks(
        self,
        sport_id: int,
        limit: int = 100,
    ) -> List[ModelPick]:
        """Get all active picks for a sport."""
        result = await self.db.execute(
            select(ModelPick)
            .where(
                and_(
                    ModelPick.sport_id == sport_id,
                    ModelPick.is_active == True,
                )
            )
            .order_by(ModelPick.confidence_score.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_picks_for_game(
        self,
        game_id: int,
        active_only: bool = True,
    ) -> List[ModelPick]:
        """Get all picks for a game."""
        conditions = [ModelPick.game_id == game_id]
        if active_only:
            conditions.append(ModelPick.is_active == True)
        
        result = await self.db.execute(
            select(ModelPick)
            .where(and_(*conditions))
            .order_by(ModelPick.confidence_score.desc())
        )
        return list(result.scalars().all())
    
    async def get_player_picks(
        self,
        player_id: int,
        active_only: bool = True,
        limit: int = 20,
    ) -> List[ModelPick]:
        """Get picks for a specific player."""
        conditions = [ModelPick.player_id == player_id]
        if active_only:
            conditions.append(ModelPick.is_active == True)
        
        result = await self.db.execute(
            select(ModelPick)
            .where(and_(*conditions))
            .order_by(ModelPick.generated_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_high_ev_picks(
        self,
        sport_id: int,
        min_ev: float = 0.05,
        limit: int = 50,
    ) -> List[ModelPick]:
        """Get picks with high expected value."""
        result = await self.db.execute(
            select(ModelPick)
            .where(
                and_(
                    ModelPick.sport_id == sport_id,
                    ModelPick.is_active == True,
                    ModelPick.expected_value >= min_ev,
                )
            )
            .order_by(ModelPick.expected_value.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_high_confidence_picks(
        self,
        sport_id: int,
        min_confidence: float = 0.7,
        limit: int = 50,
    ) -> List[ModelPick]:
        """Get picks with high confidence score."""
        result = await self.db.execute(
            select(ModelPick)
            .where(
                and_(
                    ModelPick.sport_id == sport_id,
                    ModelPick.is_active == True,
                    ModelPick.confidence_score >= min_confidence,
                )
            )
            .order_by(ModelPick.confidence_score.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_100_percent_hit_rate_picks(
        self,
        sport_id: int,
        min_games: int = 5,
    ) -> List[ModelPick]:
        """Get picks with 100% hit rate in last 5 games."""
        result = await self.db.execute(
            select(ModelPick)
            .where(
                and_(
                    ModelPick.sport_id == sport_id,
                    ModelPick.is_active == True,
                    ModelPick.hit_rate_5g == 1.0,
                )
            )
            .order_by(ModelPick.confidence_score.desc())
        )
        return list(result.scalars().all())
    
    async def get_picks_with_relations(
        self,
        sport_id: int,
        limit: int = 50,
    ) -> List[ModelPick]:
        """Get picks with related objects eagerly loaded."""
        result = await self.db.execute(
            select(ModelPick)
            .options(
                selectinload(ModelPick.game),
                selectinload(ModelPick.player),
                selectinload(ModelPick.market),
            )
            .where(
                and_(
                    ModelPick.sport_id == sport_id,
                    ModelPick.is_active == True,
                )
            )
            .order_by(ModelPick.confidence_score.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def deactivate_old_picks(
        self,
        hours: int = 24,
    ) -> int:
        """Deactivate picks older than N hours."""
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        result = await self.db.execute(
            update(ModelPick)
            .where(
                and_(
                    ModelPick.is_active == True,
                    ModelPick.generated_at < cutoff,
                )
            )
            .values(is_active=False)
        )
        await self.db.flush()
        return result.rowcount
    
    async def deactivate_picks_for_game(
        self,
        game_id: int,
    ) -> int:
        """Deactivate all picks for a game."""
        result = await self.db.execute(
            update(ModelPick)
            .where(
                and_(
                    ModelPick.game_id == game_id,
                    ModelPick.is_active == True,
                )
            )
            .values(is_active=False)
        )
        await self.db.flush()
        return result.rowcount
    
    async def create_pick(
        self,
        sport_id: int,
        game_id: int,
        market_id: int,
        side: str,
        odds: float,
        model_probability: float,
        implied_probability: float,
        expected_value: float,
        confidence_score: float,
        player_id: Optional[int] = None,
        line_value: Optional[float] = None,
        hit_rate_30d: Optional[float] = None,
        hit_rate_10g: Optional[float] = None,
        hit_rate_5g: Optional[float] = None,
        hit_rate_3g: Optional[float] = None,
    ) -> ModelPick:
        """Create a new model pick."""
        return await self.create(
            sport_id=sport_id,
            game_id=game_id,
            market_id=market_id,
            side=side,
            odds=odds,
            model_probability=model_probability,
            implied_probability=implied_probability,
            expected_value=expected_value,
            confidence_score=confidence_score,
            player_id=player_id,
            line_value=line_value,
            hit_rate_30d=hit_rate_30d,
            hit_rate_10g=hit_rate_10g,
            hit_rate_5g=hit_rate_5g,
            hit_rate_3g=hit_rate_3g,
            is_active=True,
            generated_at=datetime.now(timezone.utc),
        )
    
    async def get_pick_counts_by_sport(self) -> dict:
        """Get count of active picks per sport."""
        result = await self.db.execute(
            select(ModelPick.sport_id, func.count(ModelPick.id))
            .where(ModelPick.is_active == True)
            .group_by(ModelPick.sport_id)
        )
        return dict(result.all())
    
    async def get_recent_picks(
        self,
        sport_id: int,
        hours: int = 24,
        limit: int = 100,
    ) -> List[ModelPick]:
        """Get picks generated in the last N hours."""
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        result = await self.db.execute(
            select(ModelPick)
            .where(
                and_(
                    ModelPick.sport_id == sport_id,
                    ModelPick.generated_at >= cutoff,
                )
            )
            .order_by(ModelPick.generated_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
