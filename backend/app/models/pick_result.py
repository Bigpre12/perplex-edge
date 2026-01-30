"""PickResult model for tracking individual pick outcomes."""

from datetime import datetime
from typing import TYPE_CHECKING, Optional
from sqlalchemy import ForeignKey, Float, Boolean, Integer, Index, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.model_pick import ModelPick
    from app.models.player import Player
    from app.models.game import Game


class PickResult(Base):
    """
    Stores the outcome of each pick after the game completes.
    
    Tracks whether the pick hit or missed by comparing the actual
    player stat value against the predicted line.
    """
    
    __tablename__ = "pick_results"
    __table_args__ = (
        Index("ix_pick_results_pick", "pick_id"),
        Index("ix_pick_results_player", "player_id"),
        Index("ix_pick_results_settled", "settled_at"),
        Index("ix_pick_results_hit", "hit", "player_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    pick_id: Mapped[int] = mapped_column(ForeignKey("model_picks.id"), nullable=False, unique=True)
    player_id: Mapped[Optional[int]] = mapped_column(ForeignKey("players.id"))
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id"), nullable=False)
    
    # The actual stat value the player achieved
    actual_value: Mapped[float] = mapped_column(Float, nullable=False)
    
    # The line that was bet against (copied from pick for historical reference)
    line_value: Mapped[float] = mapped_column(Float, nullable=False)
    
    # The side that was picked (over/under)
    side: Mapped[str] = mapped_column(nullable=False)
    
    # Did the pick cash?
    hit: Mapped[bool] = mapped_column(Boolean, nullable=False)
    
    # When the result was settled
    settled_at: Mapped[datetime] = mapped_column(
        default=func.now(),
        server_default=func.now(),
    )
    
    # Closing line data (captured at game start for CLV calculation)
    closing_odds: Mapped[Optional[int]] = mapped_column(Integer)
    closing_line: Mapped[Optional[float]] = mapped_column(Float)
    
    # CLV = difference between opening and closing odds in cents of juice
    # Positive = beat the close, Negative = got worse line
    clv_cents: Mapped[Optional[float]] = mapped_column(Float)
    
    # Profit/loss for $100 unit bet
    # Win: +payout based on odds, Loss: -100
    profit_loss: Mapped[Optional[float]] = mapped_column(Float)

    # Relationships
    pick: Mapped["ModelPick"] = relationship(back_populates="result")
    player: Mapped[Optional["Player"]] = relationship(back_populates="pick_results")
    game: Mapped["Game"] = relationship(back_populates="pick_results")

    def __repr__(self) -> str:
        result = "HIT" if self.hit else "MISS"
        return f"<PickResult(pick_id={self.pick_id}, actual={self.actual_value}, line={self.line_value}, {result})>"
