"""PlayerHitRate model for aggregated player hit rate statistics."""

from datetime import datetime
from typing import TYPE_CHECKING, Optional
from sqlalchemy import ForeignKey, Float, Integer, Index, func, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.player import Player
    from app.models.sport import Sport


class PlayerHitRate(Base):
    """
    Aggregated hit rate statistics per player.
    
    This table is updated after each pick settles to maintain
    fast access to player performance metrics without needing
    to recalculate from individual results each time.
    """
    
    __tablename__ = "player_hit_rates"
    __table_args__ = (
        Index("ix_player_hit_rates_player", "player_id", unique=True),
        Index("ix_player_hit_rates_sport", "sport_id"),
        Index("ix_player_hit_rates_7d", "hit_rate_7d"),
        Index("ix_player_hit_rates_streak", "current_streak"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"), nullable=False, unique=True)
    sport_id: Mapped[int] = mapped_column(ForeignKey("sports.id"), nullable=False)
    
    # 7-day rolling stats
    hits_7d: Mapped[int] = mapped_column(Integer, default=0)
    total_7d: Mapped[int] = mapped_column(Integer, default=0)
    hit_rate_7d: Mapped[Optional[float]] = mapped_column(Float)  # null if no picks
    
    # All-time stats
    hits_all: Mapped[int] = mapped_column(Integer, default=0)
    total_all: Mapped[int] = mapped_column(Integer, default=0)
    hit_rate_all: Mapped[Optional[float]] = mapped_column(Float)  # null if no picks
    
    # Streak tracking (positive = wins, negative = losses)
    current_streak: Mapped[int] = mapped_column(Integer, default=0)
    best_streak: Mapped[int] = mapped_column(Integer, default=0)
    worst_streak: Mapped[int] = mapped_column(Integer, default=0)
    
    # Last 5 results as string for quick display (e.g., "WLWWW")
    last_5_results: Mapped[Optional[str]] = mapped_column(String(5))
    
    # Timestamps
    last_pick_at: Mapped[Optional[datetime]] = mapped_column()
    updated_at: Mapped[datetime] = mapped_column(
        default=func.now(),
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Relationships
    player: Mapped["Player"] = relationship(back_populates="hit_rate_stats")
    sport: Mapped["Sport"] = relationship(back_populates="player_hit_rates")

    def __repr__(self) -> str:
        streak_str = f"+{self.current_streak}" if self.current_streak > 0 else str(self.current_streak)
        rate = f"{self.hit_rate_7d*100:.1f}%" if self.hit_rate_7d else "N/A"
        return f"<PlayerHitRate(player_id={self.player_id}, 7d={rate}, streak={streak_str})>"
    
    def update_streak(self, hit: bool) -> None:
        """Update streak counters after a new result."""
        if hit:
            if self.current_streak >= 0:
                self.current_streak += 1
            else:
                self.current_streak = 1
            self.best_streak = max(self.best_streak, self.current_streak)
        else:
            if self.current_streak <= 0:
                self.current_streak -= 1
            else:
                self.current_streak = -1
            self.worst_streak = min(self.worst_streak, self.current_streak)
    
    def update_last_5(self, hit: bool) -> None:
        """Update the last 5 results string."""
        result = "W" if hit else "L"
        if self.last_5_results:
            self.last_5_results = (self.last_5_results + result)[-5:]
        else:
            self.last_5_results = result
