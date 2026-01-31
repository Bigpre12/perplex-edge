"""
Player Repository - Database operations for players.
"""

import logging
from typing import List, Optional

from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.player import Player
from app.data.repositories.base import BaseRepository

logger = logging.getLogger(__name__)


class PlayerRepository(BaseRepository[Player]):
    """Repository for Player database operations."""
    
    model = Player
    
    async def get_by_external_id(
        self,
        sport_id: int,
        external_player_id: str,
    ) -> Optional[Player]:
        """Get a player by external ID and sport."""
        result = await self.db.execute(
            select(Player).where(
                and_(
                    Player.sport_id == sport_id,
                    Player.external_player_id == external_player_id,
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def get_by_sport(
        self,
        sport_id: int,
        limit: int = 500,
    ) -> List[Player]:
        """Get all players for a sport."""
        result = await self.db.execute(
            select(Player)
            .where(Player.sport_id == sport_id)
            .order_by(Player.name)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_by_team(
        self,
        team_id: int,
    ) -> List[Player]:
        """Get all players for a team."""
        result = await self.db.execute(
            select(Player)
            .where(Player.team_id == team_id)
            .order_by(Player.name)
        )
        return list(result.scalars().all())
    
    async def search_by_name(
        self,
        name: str,
        sport_id: Optional[int] = None,
        limit: int = 20,
    ) -> List[Player]:
        """Search players by name (case-insensitive)."""
        conditions = [Player.name.ilike(f"%{name}%")]
        if sport_id:
            conditions.append(Player.sport_id == sport_id)
        
        result = await self.db.execute(
            select(Player)
            .where(and_(*conditions))
            .order_by(Player.name)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_with_stats(
        self,
        player_id: int,
    ) -> Optional[Player]:
        """Get a player with game stats eagerly loaded."""
        result = await self.db.execute(
            select(Player)
            .options(selectinload(Player.game_stats))
            .where(Player.id == player_id)
        )
        return result.scalar_one_or_none()
    
    async def get_with_injuries(
        self,
        player_id: int,
    ) -> Optional[Player]:
        """Get a player with injuries eagerly loaded."""
        result = await self.db.execute(
            select(Player)
            .options(selectinload(Player.injuries))
            .where(Player.id == player_id)
        )
        return result.scalar_one_or_none()
    
    async def upsert_player(
        self,
        sport_id: int,
        external_player_id: str,
        name: str,
        team_id: Optional[int] = None,
        position: Optional[str] = None,
    ) -> Player:
        """
        Insert or update a player.
        
        If player exists (by sport_id + external_player_id), update it.
        Otherwise, create a new player.
        """
        existing = await self.get_by_external_id(sport_id, external_player_id)
        
        if existing:
            # Update existing player
            existing.name = name
            if team_id is not None:
                existing.team_id = team_id
            if position is not None:
                existing.position = position
            await self.db.flush()
            return existing
        else:
            # Create new player
            return await self.create(
                sport_id=sport_id,
                external_player_id=external_player_id,
                name=name,
                team_id=team_id,
                position=position,
            )
    
    async def get_active_players(
        self,
        sport_id: int,
        team_ids: Optional[List[int]] = None,
    ) -> List[Player]:
        """
        Get active players (those with a team assigned).
        
        Optionally filter by specific team IDs.
        """
        conditions = [
            Player.sport_id == sport_id,
            Player.team_id.isnot(None),
        ]
        if team_ids:
            conditions.append(Player.team_id.in_(team_ids))
        
        result = await self.db.execute(
            select(Player)
            .where(and_(*conditions))
            .order_by(Player.team_id, Player.name)
        )
        return list(result.scalars().all())
    
    async def get_by_ids(
        self,
        player_ids: List[int],
    ) -> List[Player]:
        """Get multiple players by their IDs."""
        if not player_ids:
            return []
        
        result = await self.db.execute(
            select(Player)
            .where(Player.id.in_(player_ids))
        )
        return list(result.scalars().all())
    
    async def update_team(
        self,
        player_id: int,
        team_id: int,
    ) -> Optional[Player]:
        """Update a player's team."""
        return await self.update_by_id(player_id, team_id=team_id)
