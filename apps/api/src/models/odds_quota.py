"""Persisted TheOddsAPI quota / exhaustion state (monthly)."""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, false
from sqlalchemy.sql import func

from db.base import Base


class OddsApiUsage(Base):
    """
    One row per calendar month (YYYY-MM).
    Synced from TheOddsAPI response headers (x-requests-remaining, x-requests-used).
    """

    __tablename__ = "odds_api_usage"

    id = Column(Integer, primary_key=True, index=True)
    month = Column(String(7), unique=True, nullable=False, index=True)
    requests_used = Column(Integer, nullable=False, server_default="0")
    requests_remaining = Column(Integer, nullable=True)
    quota_exhausted = Column(Boolean, nullable=False, server_default=false())
    sport = Column(String, nullable=True)
    market = Column(String, nullable=True)
    endpoint = Column(String, nullable=True)
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
