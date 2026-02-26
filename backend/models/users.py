from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    
    # Tier limits (free, pro, whale)
    subscription_tier = Column(String, default="free")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    
    # Overall ROI tracking
    lifetime_roi = Column(Integer, default=0)
    
    # Webhook Configurations
    discord_webhook_url = Column(String, nullable=True)
    telegram_bot_token = Column(String, nullable=True)
    telegram_chat_id = Column(String, nullable=True)

class PushSubscription(Base):
    __tablename__ = "pushsubscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    endpoint = Column(String, unique=True)
    p256dh = Column(String)
    auth = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class APIKey(Base):
    __tablename__ = "apikeys"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    key_hash = Column(String, unique=True)
    label = Column(String)
    requests_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
