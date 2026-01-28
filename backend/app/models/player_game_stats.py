from datetime import datetime
from typing import TYPE_CHECKING, Optional
from sqlalchemy import ForeignKey, String, Float, Index, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.player import Player
    from app.models.game import Game


class PlayerGameStats(Base):
    """Player game statistics model."""
    
    __tablename__ = "player_game_stats"
    __table_args__ = (
        Index("ix_player_game_stats_player_game", "player_id", "game_id"),
        Index("ix_player_game_stats_stat_type", "stat_type"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"), nullable=False)
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id"), nullable=False)
    stat_type: Mapped[str] = mapped_column(String(50), nullable=False)
    # stat_type: PTS, REB, AST, 3PM, BLK, STL, MIN, FG_PCT, etc.
    value: Mapped[float] = mapped_column(Float, nullable=False)
    minutes: Mapped[Optional[float]] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(
        default=func.now(),
        server_default=func.now(),
    )

    # Relationships
    player: Mapped["Player"] = relationship(back_populates="game_stats")
    game: Mapped["Game"] = relationship(back_populates="player_stats")

    def __repr__(self) -> str:
        return f"<PlayerGameStats(id={self.id}, player_id={self.player_id}, stat='{self.stat_type}', value={self.value})>"
