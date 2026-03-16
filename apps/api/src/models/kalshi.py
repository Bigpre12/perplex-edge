# apps/api/src/models/kalshi.py
from sqlalchemy import Column, String, Numeric, DateTime, BigInteger, Integer
from sqlalchemy.sql import func
from db.base import Base

class KalshiMarket(Base):
    """
    Institutional Kalshi trading markets.
    """
    __tablename__ = "kalshi_markets"
    
    id = Column(String, primary_key=True)  # Kalshi ticker
    sport = Column(String, nullable=True)
    title = Column(String, nullable=False)
    category = Column(String, nullable=True)
    yes_price = Column(Numeric, nullable=True)
    no_price = Column(Numeric, nullable=True)
    volume = Column(BigInteger, nullable=True)
    open_interest = Column(BigInteger, nullable=True)
    status = Column(String, nullable=True)
    close_time = Column(DateTime(timezone=True), nullable=True)
    synced_at = Column(DateTime(timezone=True), server_default=func.now())

class KalshiOrder(Base):
    """
    Kalshi orders and trade executions.
    """
    __tablename__ = "kalshi_orders"
    
    id = Column(BigInteger, primary_key=True)
    user_id = Column(String, nullable=False, index=True)
    market_id = Column(String, nullable=False)
    side = Column(String, nullable=False)           # 'yes' or 'no'
    order_type = Column(String, nullable=False)     # 'market' or 'limit'
    contracts = Column(Integer, nullable=False)
    limit_price = Column(Numeric, nullable=True)
    fill_price = Column(Numeric, nullable=True)
    status = Column(String, nullable=False)         # 'pending', 'filled', 'cancelled'
    kalshi_order_id = Column(String, unique=True, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
