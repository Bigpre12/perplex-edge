from datetime import datetime
from typing import TYPE_CHECKING, Optional
from sqlalchemy import ForeignKey, String, Boolean, Float, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.sport import Sport
    from app.models.player import Player


class Injury(Base):
    """Injury model for player injury status."""
    
    __tablename__ = "injuries"
    __table_args__ = (
        Index("ix_injuries_player", "player_id"),
        Index("ix_injuries_updated", "updated_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    sport_id: Mapped[int] = mapped_column(ForeignKey("sports.id"), nullable=False)
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    # status: OUT, DOUBTFUL, QUESTIONABLE, PROBABLE, AVAILABLE, GTD
    status_detail: Mapped[Optional[str]] = mapped_column(String(500))
    # status_detail: "Ankle - Sprain", "Rest", etc.
    is_starter_flag: Mapped[Optional[bool]] = mapped_column(Boolean)
    probability: Mapped[Optional[float]] = mapped_column(Float)
    # probability of playing (0.0 - 1.0)
    source: Mapped[Optional[str]] = mapped_column(String(100))
    updated_at: Mapped[datetime] = mapped_column(nullable=False)

    # Relationships
    sport: Mapped["Sport"] = relationship(back_populates="injuries")
    player: Mapped["Player"] = relationship(back_populates="injuries")

    def __repr__(self) -> str:
        return f"<Injury(id={self.id}, player_id={self.player_id}, status='{self.status}')>"


# =============================================================================
# Injury Status Constants
# =============================================================================

# Statuses that should be excluded from picks/props
# Players with these statuses should not appear in recommendations
EXCLUDED_INJURY_STATUSES = ["OUT", "DOUBTFUL", "QUESTIONABLE", "GTD", "DAY_TO_DAY"]
