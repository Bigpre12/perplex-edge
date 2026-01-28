"""HistoricalPerformance model for tracking player betting performance."""
from sqlalchemy import String, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class HistoricalPerformance(Base, TimestampMixin):
    """Historical performance model for tracking player betting stats over time."""
    
    __tablename__ = "historical_performances"

    id: Mapped[int] = mapped_column(primary_key=True)
    player_name: Mapped[str] = mapped_column(String(200), nullable=False)
    stat_type: Mapped[str] = mapped_column(String(50), nullable=False)  # PTS, REB, AST, etc.
    total_picks: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    hits: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    misses: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    hit_rate_percentage: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    avg_ev: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    def __repr__(self) -> str:
        return f"<HistoricalPerformance(id={self.id}, player='{self.player_name}', stat='{self.stat_type}', hit_rate={self.hit_rate_percentage})>"
