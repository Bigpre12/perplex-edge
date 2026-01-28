from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import ForeignKey, String, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.sport import Sport
    from app.models.line import Line
    from app.models.model_pick import ModelPick


class Market(Base, TimestampMixin):
    """Market model for bet types."""
    
    __tablename__ = "markets"
    __table_args__ = (
        Index("ix_markets_sport_type", "sport_id", "market_type", "stat_type"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    sport_id: Mapped[int] = mapped_column(ForeignKey("sports.id"), nullable=False)
    market_type: Mapped[str] = mapped_column(String(50), nullable=False)
    # market_type values: spread, total, moneyline, player_prop
    stat_type: Mapped[Optional[str]] = mapped_column(String(50))
    # stat_type for props: PTS, REB, AST, 3PM, BLK, STL, etc.
    description: Mapped[Optional[str]] = mapped_column(String(200))

    # Relationships
    sport: Mapped["Sport"] = relationship(back_populates="markets")
    lines: Mapped[List["Line"]] = relationship(back_populates="market")
    model_picks: Mapped[List["ModelPick"]] = relationship(back_populates="market")

    def __repr__(self) -> str:
        return f"<Market(id={self.id}, type='{self.market_type}', stat='{self.stat_type}')>"
