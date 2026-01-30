"""GameResult model for tracking final game scores and settlement data from OddsPapi."""

from datetime import datetime
from typing import TYPE_CHECKING, Optional
from sqlalchemy import ForeignKey, String, Integer, Index, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.game import Game


class GameResult(Base, TimestampMixin):
    """
    Stores final game scores and settlement data from OddsPapi.
    
    Used to determine pick outcomes and calculate hit rates.
    Links to the Game model via game_id.
    """
    
    __tablename__ = "game_results"
    __table_args__ = (
        Index("ix_game_results_game", "game_id", unique=True),
        Index("ix_game_results_external", "external_fixture_id"),
        Index("ix_game_results_settled", "settled_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id"), nullable=False, unique=True)
    
    # OddsPapi identifier
    external_fixture_id: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # Final scores
    home_score: Mapped[int] = mapped_column(Integer, nullable=False)
    away_score: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Period scores (stored as JSON-like string for flexibility)
    # Format: "Q1:25-22,Q2:30-28,Q3:27-25,Q4:28-30" or similar
    period_scores: Mapped[Optional[str]] = mapped_column(String(500))
    
    # Settlement status
    is_settled: Mapped[bool] = mapped_column(default=True)
    settled_at: Mapped[datetime] = mapped_column(
        default=func.now(),
        server_default=func.now(),
    )

    # Relationships
    game: Mapped["Game"] = relationship()

    def __repr__(self) -> str:
        return f"<GameResult(game_id={self.game_id}, score={self.home_score}-{self.away_score})>"
    
    @property
    def total_score(self) -> int:
        """Get total combined score."""
        return self.home_score + self.away_score
    
    @property
    def home_win(self) -> bool:
        """Check if home team won."""
        return self.home_score > self.away_score
    
    @property
    def away_win(self) -> bool:
        """Check if away team won."""
        return self.away_score > self.home_score
    
    @property
    def spread(self) -> float:
        """Get the spread (positive = home won by X, negative = away won by X)."""
        return self.home_score - self.away_score
