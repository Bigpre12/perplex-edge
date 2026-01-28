"""Pick model for betting picks."""
from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey, String, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class Pick(Base, TimestampMixin):
    """Pick model for storing betting picks."""
    
    __tablename__ = "picks"

    id: Mapped[int] = mapped_column(primary_key=True)
    game_id: Mapped[Optional[int]] = mapped_column(ForeignKey("games.id"), nullable=True)
    pick_type: Mapped[str] = mapped_column(String(50), nullable=False)  # spread, total, player_prop
    player_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    stat_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # PTS, REB, AST, etc.
    line: Mapped[float] = mapped_column(Float, nullable=False)
    odds: Mapped[int] = mapped_column(Integer, nullable=False)
    model_probability: Mapped[float] = mapped_column(Float, nullable=False)
    implied_probability: Mapped[float] = mapped_column(Float, nullable=False)
    ev_percentage: Mapped[float] = mapped_column(Float, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    hit_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    def __repr__(self) -> str:
        return f"<Pick(id={self.id}, type='{self.pick_type}', player='{self.player_name}')>"
