"""Watchlist model for saving filter presets and tracking new matches."""

from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, Boolean, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class Watchlist(Base, TimestampMixin):
    """
    User-defined filter presets for tracking specific prop angles.
    
    Examples:
    - "NBA Assists Unders" with filters: sport_id=30, stat_type=AST, side=under, min_ev=0.05
    - "NFL Receiving Yards" with filters: sport_id=31, stat_type=receiving_yards, min_confidence=0.60
    
    The filters dict stores all filter criteria that can be applied to the
    player props endpoint.
    """
    
    __tablename__ = "watchlists"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    
    # User-defined name
    name: Mapped[str] = mapped_column(String(100))
    
    # Filter criteria stored as JSON
    # Example: {"sport_id": 30, "stat_type": "AST", "side": "under", "min_ev": 0.05}
    filters: Mapped[dict] = mapped_column(JSON, default=dict)
    
    # Alert settings
    alert_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    alert_discord_webhook: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    alert_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Tracking
    last_check_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    last_match_count: Mapped[int] = mapped_column(Integer, default=0)
    last_notified_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    
    # Sport reference (for quick filtering)
    sport_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("sports.id"), nullable=True
    )
    
    def __repr__(self):
        return f"<Watchlist {self.id}: {self.name}>"
