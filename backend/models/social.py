from sqlalchemy import Column, Integer, String, DateTime, JSON, Text
from sqlalchemy.sql import func
from database import Base

class SharedIntel(Base):
    __tablename__ = "sharedintel"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    slip_id = Column(Integer, nullable=True) # Reference to BetSlip if sharing a slip
    
    title = Column(String)
    content = Column(Text, nullable=True) # Analysis/Description
    
    likes_count = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class PublicSlate(Base):
    __tablename__ = "publicslates"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(Text, nullable=True)
    picks = Column(JSON, nullable=True)  # Array of pick objects
    published_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(Integer, nullable=True)

class OddsAlert(Base):
    __tablename__ = "oddsalerts"
    
    id = Column(Integer, primary_key=True, index=True)
    prop_id = Column(Integer, index=True)
    alert_type = Column(String) # 'sharp_money', 'steam_move', 'injury_impact'
    message = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
