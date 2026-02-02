"""Shared card model for public shareable parlay cards."""

from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, Float, JSON, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class SharedCard(Base, TimestampMixin):
    """
    A shareable parlay card that can be viewed via public URL.
    
    Used for social sharing and virality - "Look at this edge I found!"
    """
    
    __tablename__ = "shared_cards"
    
    id: Mapped[str] = mapped_column(String(12), primary_key=True)  # Short hash ID
    
    # Card metadata
    platform: Mapped[str] = mapped_column(String(50))  # prizepicks, fliff, underdog, sportsbook
    sport_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Parlay data (serialized)
    legs: Mapped[dict] = mapped_column(JSON)  # List of leg dicts
    leg_count: Mapped[int] = mapped_column(Integer)
    
    # Metrics at time of sharing
    total_odds: Mapped[int] = mapped_column(Integer)
    decimal_odds: Mapped[float] = mapped_column(Float)
    parlay_probability: Mapped[float] = mapped_column(Float)
    parlay_ev: Mapped[float] = mapped_column(Float)
    overall_grade: Mapped[str] = mapped_column(String(1))
    label: Mapped[str] = mapped_column(String(10))  # LOCK, PLAY, SKIP
    
    # Kelly sizing
    kelly_suggested_units: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    kelly_risk_level: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    # Tracking
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Optional: outcome tracking after settlement
    settled: Mapped[bool] = mapped_column(Boolean, default=False)
    won: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    settled_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    
    def __repr__(self):
        return f"<SharedCard {self.id}: {self.leg_count}-leg {self.platform}>"
