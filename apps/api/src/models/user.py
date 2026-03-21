from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON
from sqlalchemy.sql import func
from db.base import Base

class User(Base):
    __tablename__ = "users"
    __table_args__ = {"extend_existing": True}
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    auth_id = Column(String, unique=True, index=True, nullable=True) # Supabase UUID
    hashed_password = Column(String)
    
    # Tier limits (free, pro, elite)
    subscription_tier = Column(String, default="free")
    stripe_customer_id = Column(String, nullable=True, index=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    role = Column(String, default="user")
    
    @property
    def tier(self):
        return (self.subscription_tier or "free").lower()
    
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
    tier = Column(String, default="free") # Sprint 20: 'free', 'pro', 'enterprise'
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    rate_limit_per_hour = Column(Integer, default=100)
    requests_this_hour = Column(Integer, default=0)
    last_reset = Column(DateTime(timezone=True), server_default=func.now())
    total_requests = Column(Integer, default=0)
    last_used = Column(DateTime(timezone=True), nullable=True)
    label = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class UserOverride(Base):
    __tablename__ = "user_overrides"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    tier = Column(String, default="elite", nullable=False)
    granted_by = Column(String, default="admin")
    note = Column(String, nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True) # NULL = never expires
    created_at = Column(DateTime(timezone=True), server_default=func.now())
