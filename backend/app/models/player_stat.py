"""PlayerStat model for tracking actual player statistics."""
from datetime import datetime

from sqlalchemy import String, Float, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class PlayerStat(Base, TimestampMixin):
    """Player stat model for tracking actual game statistics."""
    
    __tablename__ = "player_stats"

    id: Mapped[int] = mapped_column(primary_key=True)
    player_name: Mapped[str] = mapped_column(String(200), nullable=False)
    team: Mapped[str] = mapped_column(String(100), nullable=False)
    opponent: Mapped[str] = mapped_column(String(100), nullable=False)
    date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    stat_type: Mapped[str] = mapped_column(String(50), nullable=False)  # PTS, REB, AST, etc.
    actual_value: Mapped[float] = mapped_column(Float, nullable=False)
    line: Mapped[float] = mapped_column(Float, nullable=False)
    result: Mapped[str] = mapped_column(String(20), nullable=False)  # hit, miss

    def __repr__(self) -> str:
        return f"<PlayerStat(id={self.id}, player='{self.player_name}', stat='{self.stat_type}', result='{self.result}')>"
