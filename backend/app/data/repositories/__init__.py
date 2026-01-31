"""
Repository Layer - Database Operations Only.

Repositories handle all database CRUD operations.
They do NOT:
- Fetch from external APIs (that's the provider layer)
- Cache data (that's the service/cache layer)
- Handle business logic (that's the service layer)

Each repository:
- Works with SQLAlchemy models
- Provides async methods for CRUD
- Uses consistent error handling
"""

from app.data.repositories.base import BaseRepository
from app.data.repositories.games import GameRepository
from app.data.repositories.lines import LineRepository
from app.data.repositories.players import PlayerRepository
from app.data.repositories.picks import PickRepository

__all__ = [
    "BaseRepository",
    "GameRepository",
    "LineRepository",
    "PlayerRepository",
    "PickRepository",
]
