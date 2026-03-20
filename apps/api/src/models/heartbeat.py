from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.sql import func
from db.base import Base

class Heartbeat(Base):
    __tablename__ = "heartbeats"
    
    id = Column(Integer, primary_key=True, index=True)
    feed_name = Column(String, index=True, unique=True)
    last_run_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_success_at = Column(DateTime(timezone=True))
    rows_written_today = Column(Integer, default=0)
    error_count_today = Column(Integer, default=0)
    status = Column(String, default="unknown") # "ok", "error", "stale"
    meta = Column(JSON, nullable=True) # Any extra context
