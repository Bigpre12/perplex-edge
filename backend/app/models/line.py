from datetime import datetime
from typing import TYPE_CHECKING, Optional
from sqlalchemy import ForeignKey, String, Float, Boolean, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.game import Game
    from app.models.market import Market
    from app.models.player import Player


class Line(Base):
    """Line model for odds/betting lines."""
    
    __tablename__ = "lines"
    __table_args__ = (
        Index("ix_lines_game_market", "game_id", "market_id"),
        Index("ix_lines_current", "is_current", "game_id"),
        Index("ix_lines_fetched_at", "fetched_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id"), nullable=False)
    market_id: Mapped[int] = mapped_column(ForeignKey("markets.id"), nullable=False)
    player_id: Mapped[Optional[int]] = mapped_column(ForeignKey("players.id"))
    sportsbook: Mapped[str] = mapped_column(String(50), nullable=False)
    line_value: Mapped[Optional[float]] = mapped_column(Float)
    # line_value: spread (-3.5), total (220.5), prop line (24.5)
    odds: Mapped[float] = mapped_column(Float, nullable=False)
    # American odds: -110, +150, etc.
    side: Mapped[str] = mapped_column(String(20), nullable=False)
    # side: home, away, over, under
    is_current: Mapped[bool] = mapped_column(Boolean, default=True)
    fetched_at: Mapped[datetime] = mapped_column(nullable=False)

    # Relationships
    game: Mapped["Game"] = relationship(back_populates="lines")
    market: Mapped["Market"] = relationship(back_populates="lines")
    player: Mapped[Optional["Player"]] = relationship(back_populates="lines")

    def __repr__(self) -> str:
        return f"<Line(id={self.id}, sportsbook='{self.sportsbook}', odds={self.odds})>"
