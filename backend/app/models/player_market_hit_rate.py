"""PlayerMarketHitRate model for per-player, per-market hit rate statistics."""

from datetime import datetime
from typing import TYPE_CHECKING, Optional
from sqlalchemy import ForeignKey, Float, Integer, Index, func, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.player import Player
    from app.models.sport import Sport


class PlayerMarketHitRate(Base):
    """
    Per-player, per-market hit rate statistics.
    
    Tracks performance for specific stat types like:
    - PTS OVER, PTS UNDER
    - REB OVER, REB UNDER
    - 3PM OVER, 3PM UNDER
    - AST OVER, AST UNDER
    - PRA OVER, PRA UNDER
    
    This enables market-aware hot/cold player lists like:
    "CJ McCollum – 6/6 on 3PM OVER (100% hit rate)"
    """
    
    __tablename__ = "player_market_hit_rates"
    __table_args__ = (
        UniqueConstraint("player_id", "sport_id", "market", "side", name="uq_player_market_side"),
        Index("ix_player_market_hit_rates_player", "player_id"),
        Index("ix_player_market_hit_rates_sport", "sport_id"),
        Index("ix_player_market_hit_rates_market", "market"),
        Index("ix_player_market_hit_rates_streak", "current_streak"),
        Index("ix_player_market_hit_rates_7d", "hit_rate_7d"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"), nullable=False)
    sport_id: Mapped[int] = mapped_column(ForeignKey("sports.id"), nullable=False)
    market: Mapped[str] = mapped_column(String(50), nullable=False)  # PTS, REB, AST, 3PM, PRA, etc.
    side: Mapped[str] = mapped_column(String(10), nullable=False)    # 'over' or 'under'
    
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
    player: Mapped["Player"] = relationship(back_populates="market_hit_rates")
    sport: Mapped["Sport"] = relationship(back_populates="player_market_hit_rates")

    def __repr__(self) -> str:
        streak_str = f"+{self.current_streak}" if self.current_streak > 0 else str(self.current_streak)
        rate = f"{self.hit_rate_7d*100:.1f}%" if self.hit_rate_7d else "N/A"
        return f"<PlayerMarketHitRate(player_id={self.player_id}, {self.market} {self.side.upper()}, 7d={rate}, streak={streak_str})>"
    
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
    
    def recalculate_hit_rates(self) -> None:
        """Recalculate hit rates from counts."""
        self.hit_rate_7d = self.hits_7d / self.total_7d if self.total_7d > 0 else None
        self.hit_rate_all = self.hits_all / self.total_all if self.total_all > 0 else None
