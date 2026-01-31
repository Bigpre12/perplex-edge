"""
Base Repository class for database operations.

Provides common CRUD patterns that all repositories inherit.
"""

import logging
from typing import Any, Generic, List, Optional, Type, TypeVar

from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

# Type variable for SQLAlchemy models
ModelT = TypeVar("ModelT")


class BaseRepository(Generic[ModelT]):
    """
    Base repository with common CRUD operations.
    
    Usage:
        class GameRepository(BaseRepository[Game]):
            model = Game
    """
    
    model: Type[ModelT]
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, id: int) -> Optional[ModelT]:
        """Get a single record by ID."""
        result = await self.db.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(self, limit: int = 100, offset: int = 0) -> List[ModelT]:
        """Get all records with pagination."""
        result = await self.db.execute(
            select(self.model).limit(limit).offset(offset)
        )
        return list(result.scalars().all())
    
    async def create(self, **kwargs) -> ModelT:
        """Create a new record."""
        instance = self.model(**kwargs)
        self.db.add(instance)
        await self.db.flush()
        await self.db.refresh(instance)
        return instance
    
    async def create_many(self, items: List[dict]) -> List[ModelT]:
        """Create multiple records."""
        instances = [self.model(**item) for item in items]
        self.db.add_all(instances)
        await self.db.flush()
        return instances
    
    async def update_by_id(self, id: int, **kwargs) -> Optional[ModelT]:
        """Update a record by ID."""
        await self.db.execute(
            update(self.model)
            .where(self.model.id == id)
            .values(**kwargs)
        )
        await self.db.flush()
        return await self.get_by_id(id)
    
    async def delete_by_id(self, id: int) -> bool:
        """Delete a record by ID. Returns True if deleted."""
        result = await self.db.execute(
            delete(self.model).where(self.model.id == id)
        )
        await self.db.flush()
        return result.rowcount > 0
    
    async def exists(self, id: int) -> bool:
        """Check if a record exists by ID."""
        result = await self.db.execute(
            select(self.model.id).where(self.model.id == id)
        )
        return result.scalar_one_or_none() is not None
    
    async def count(self) -> int:
        """Get total count of records."""
        from sqlalchemy import func
        result = await self.db.execute(
            select(func.count()).select_from(self.model)
        )
        return result.scalar_one()
