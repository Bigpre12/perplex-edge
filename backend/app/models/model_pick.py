from datetime import datetime
from typing import TYPE_CHECKING, Optional
from sqlalchemy import ForeignKey, String, Float, Boolean, Index, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.sport import Sport
    from app.models.game import Game
    from app.models.player import Player
    from app.models.market import Market


class ModelPick(Base):
    """Model pick/prediction model."""
    
    __tablename__ = "model_picks"
    __table_args__ = (
        Index("ix_model_picks_game", "game_id"),
        Index("ix_model_picks_active", "is_active", "sport_id"),
        Index("ix_model_picks_generated", "generated_at"),
        Index("ix_model_picks_confidence", "confidence_score"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    sport_id: Mapped[int] = mapped_column(ForeignKey("sports.id"), nullable=False)
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id"), nullable=False)
    player_id: Mapped[Optional[int]] = mapped_column(ForeignKey("players.id"))
    market_id: Mapped[int] = mapped_column(ForeignKey("markets.id"), nullable=False)
    
    # Pick details
    side: Mapped[str] = mapped_column(String(20), nullable=False)
    # side: home, away, over, under
    line_value: Mapped[Optional[float]] = mapped_column(Float)
    odds: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Model metrics
    model_probability: Mapped[float] = mapped_column(Float, nullable=False)
    # Model's predicted probability of the pick hitting (0.0 - 1.0)
    implied_probability: Mapped[float] = mapped_column(Float, nullable=False)
    # Implied probability from odds (0.0 - 1.0)
    expected_value: Mapped[float] = mapped_column(Float, nullable=False)
    # EV = (model_prob * payout) - (1 - model_prob)
    
    # Historical performance
    hit_rate_30d: Mapped[Optional[float]] = mapped_column(Float)
    # Hit rate for similar picks over last 30 days
    hit_rate_10g: Mapped[Optional[float]] = mapped_column(Float)
    # Hit rate for player over last 10 games (for props)
    
    # Confidence and status
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False)
    # Overall confidence score (0.0 - 1.0)
    generated_at: Mapped[datetime] = mapped_column(
        default=func.now(),
        server_default=func.now(),
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    sport: Mapped["Sport"] = relationship(back_populates="model_picks")
    game: Mapped["Game"] = relationship(back_populates="model_picks")
    player: Mapped[Optional["Player"]] = relationship(back_populates="model_picks")
    market: Mapped["Market"] = relationship(back_populates="model_picks")

    def __repr__(self) -> str:
        return f"<ModelPick(id={self.id}, side='{self.side}', ev={self.expected_value:.2f}, conf={self.confidence_score:.2f})>"
