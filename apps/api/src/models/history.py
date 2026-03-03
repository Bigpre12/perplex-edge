from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from database import Base

class PropHistory(Base):
    __tablename__ = "prop_history"
    
    id = Column(Integer, primary_key=True, index=True)
    prop_line_id = Column(Integer, ForeignKey("proplines.id"), index=True)
    
    old_line = Column(Float)
    new_line = Column(Float)
    
    old_odds_over = Column(Integer)
    new_odds_over = Column(Integer)
    
    old_odds_under = Column(Integer)
    new_odds_under = Column(Integer)
    
    change_type = Column(String)  # 'line_move', 'odds_move', 'steam'
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
