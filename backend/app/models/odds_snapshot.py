"""OddsSnapshot model for tracking historical odds movements from OddsPapi."""

from datetime import datetime
from typing import TYPE_CHECKING, Optional
from sqlalchemy import ForeignKey, String, Float, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.game import Game
    from app.models.market import Market
    from app.models.player import Player


class OddsSnapshot(Base, TimestampMixin):
    """
    Stores historical odds snapshots from OddsPapi.
    
    Tracks how odds move over time for analytics and trend analysis.
    Each record represents a single odds point at a specific time.
    """
    
    __tablename__ = "odds_snapshots"
    __table_args__ = (
        Index("ix_odds_snapshots_game", "game_id"),
        Index("ix_odds_snapshots_player", "player_id"),
        Index("ix_odds_snapshots_snapshot_at", "snapshot_at"),
        Index("ix_odds_snapshots_game_market", "game_id", "market_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id"), nullable=False)
    market_id: Mapped[int] = mapped_column(ForeignKey("markets.id"), nullable=False)
    player_id: Mapped[Optional[int]] = mapped_column(ForeignKey("players.id"))
    
    # OddsPapi identifiers
    external_fixture_id: Mapped[str] = mapped_column(String(100), nullable=False)
    external_market_id: Mapped[Optional[str]] = mapped_column(String(100))
    external_outcome_id: Mapped[Optional[str]] = mapped_column(String(100))
    
    # Bookmaker info
    bookmaker: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Odds data
    line_value: Mapped[Optional[float]] = mapped_column(Float)
    price: Mapped[float] = mapped_column(Float, nullable=False)  # Decimal odds
    american_odds: Mapped[Optional[float]] = mapped_column(Float)  # Converted American odds
    
    # Metadata
    side: Mapped[Optional[str]] = mapped_column(String(20))  # over, under, home, away
    is_active: Mapped[bool] = mapped_column(default=True)
    snapshot_at: Mapped[datetime] = mapped_column(nullable=False)  # When odds were recorded by OddsPapi

    # Relationships
    game: Mapped["Game"] = relationship()
    market: Mapped["Market"] = relationship()
    player: Mapped[Optional["Player"]] = relationship()

    def __repr__(self) -> str:
        return f"<OddsSnapshot(id={self.id}, game={self.game_id}, price={self.price}, at={self.snapshot_at})>"
    
    @property
    def implied_probability(self) -> float:
        """Calculate implied probability from decimal odds."""
        if self.price and self.price > 0:
            return 1 / self.price
        return 0.0
