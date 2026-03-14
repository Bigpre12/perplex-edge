from sqlalchemy import Column, Integer, String, DateTime, Float
from sqlalchemy.sql import func
from database import Base

class Contest(Base):
    __tablename__ = "contests"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String, nullable=True)
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))
    entry_fee = Column(Float, default=0.0)
    prize_pool = Column(Float, default=0.0)
    prize_description = Column(String, nullable=True)
    required_legs = Column(Integer, default=5)
    entry_count = Column(Integer, default=0)
    status = Column(String, default="upcoming") # upcoming, active, completed

    @property
    def is_active(self):
        from datetime import datetime
        now = datetime.utcnow()
        return self.status == "active" and (self.end_date is None or self.end_date > now)

class ContestEntry(Base):
    __tablename__ = "contestentries"
    
    id = Column(Integer, primary_key=True, index=True)
    contest_id = Column(Integer, index=True)
    user_id = Column(Integer, index=True)
    display_name = Column(String, nullable=True)
    prop_ids_json = Column(String, nullable=True) # JSON list of prop IDs
    current_score = Column(Float, default=0.0)
    hits = Column(Integer, default=0)
    total_legs = Column(Integer, default=0)
    rank = Column(Integer, nullable=True)
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
