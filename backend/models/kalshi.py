from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean
from sqlalchemy.sql import func
from database import Base

class KalshiMarket(Base):
    """Integration for predictive markets on Kalshi"""
    __tablename__ = "kalshimarkets"
    
    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String, unique=True, index=True)
    title = Column(String)
    category = Column(String)
    
    yes_price = Column(Float)
    no_price = Column(Float)
    volume = Column(Integer)
    
    is_active = Column(Boolean, default=True)
    close_date = Column(DateTime(timezone=True))
    last_updated = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
