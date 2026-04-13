from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.sql import func
from db.base import Base

class SavedSystem(Base):
    __tablename__ = "saved_systems"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    name = Column(String, index=True)
    config = Column(JSON, nullable=False) # JSONB in Postgres, JSON in SQLAlchemy
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
