from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, JSON, Column as SAColumn
from sqlalchemy.orm import Relationship
from sqlalchemy.sql import func
from db.base import Base
from typing import Optional, List
from datetime import datetime as dt
try:
    from sqlmodel import SQLModel, Field
except ImportError:
    # Fallback if sqlmodel is not available
    class SQLModel: pass
    def Field(**kwargs): return None

class BrainSystemState(Base):
    __tablename__ = "brain_system_state"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    cycle_count = Column(Integer, default=0)
    overall_status = Column(String(20), default='initializing')
    heals_attempted = Column(Integer, default=0)
    heals_succeeded = Column(Integer, default=0)
    consecutive_failures = Column(Integer, default=0)
    sport_priority = Column(String(20), default='balanced')
    quota_budget = Column(Integer, default=100)
    auto_commit_enabled = Column(Boolean, default=True)
    git_commits_made = Column(Integer, default=0)
    betting_opportunities_found = Column(Integer, default=0)
    strong_bets_identified = Column(Integer, default=0)
    last_betting_scan = Column(DateTime(timezone=True))
    top_betting_opportunities = Column(JSON)
    last_cycle_duration_ms = Column(Integer)
    uptime_hours = Column(Float, default=0.0)

class ModelPick(Base):
    __tablename__ = "model_picks"
    
    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(String, index=True)
    player_name = Column(String)
    stat_type = Column(String)
    line = Column(Float)
    side = Column(String)
    odds = Column(Float)
    ev_percentage = Column(Float)
    confidence = Column(Float)
    hit_rate = Column(Float)
    sportsbook = Column(String)
    sport_key = Column(String, index=True)
    sport_id = Column(Integer, index=True)
    status = Column(String, default='pending')
    won = Column(Boolean, nullable=True)
    actual_value = Column(Float, nullable=True)
    profit_loss = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # CLV Enrichment Columns (Sprint 12/Brain Sync)
    closing_odds = Column(Float, nullable=True)
    clv_percentage = Column(Float, nullable=True)
    roi_percentage = Column(Float, nullable=True)
    opening_odds = Column(Float, nullable=True)
    line_movement = Column(Float, nullable=True)
    sharp_money_indicator = Column(Float, nullable=True)
    best_book_odds = Column(Float, nullable=True)
    best_book_name = Column(String(50), nullable=True)
    ev_improvement = Column(Float, nullable=True)
    
    team = Column(String, nullable=True)
    model_probability = Column(Float, nullable=True)
    implied_probability = Column(Float, nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class SteamSnapshot(Base):
    __tablename__ = "steam_snapshots"
    
    id = Column(String, primary_key=True, index=True) # UUID string
    sport = Column(String)
    player = Column(String)
    stat_type = Column(String)
    line = Column(Float)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    sportsbook = Column(String)
    game = Column(String)

class BrainLog(Base):
    __tablename__ = "brain_log"
    
    id = Column(String, primary_key=True, index=True) # UUID string
    sport = Column(String)
    player = Column(String)
    stat_type = Column(String)
    line = Column(Float)
    signal = Column(String)
    brain_score = Column(Integer)
    reason = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    result = Column(String, default='PENDING')

# --- LAYER 1: SHARP MONEY ---
class SharpSignal(Base):
    __tablename__ = "sharp_signals"
    
    id = Column(Integer, primary_key=True, index=True)
    sport = Column(String, index=True)
    event_id = Column(String, index=True)
    market_key = Column(String)
    selection = Column(String) # Player name or Team
    signal_type = Column(String) # 'steam', 'rlm', 'key_cross'
    severity = Column(Float) # Movement magnitude
    bookmakers_involved = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# --- LAYER 4: CORRELATION ---
class PropCorrelation(Base):
    __tablename__ = "prop_correlations"
    
    id = Column(Integer, primary_key=True, index=True)
    sport = Column(String, index=True)
    player_a = Column(String)
    player_b = Column(String)
    stat_a = Column(String)
    stat_b = Column(String)
    correlation_coefficient = Column(Float)
    recommendation = Column(String) # 'Pair', 'Avoid'
    updated_at = Column(DateTime(timezone=True), server_default=func.now())

# --- LAYER 5: CLV ---
class CLVRecord(Base):
    __tablename__ = "clv_tracking"
    __table_args__ = {"extend_existing": True}
    
    id = Column(Integer, primary_key=True, index=True)
    sport = Column(String, index=True)
    event_id = Column(String, index=True)
    user_id = Column(String, index=True, nullable=True) # From analytical
    bet_id = Column(Integer, index=True, nullable=True) # From analytical
    market_key = Column(String)
    selection = Column(String)
    player_name = Column(String, index=True, nullable=True) # Alias for selection
    stat_type = Column(String, nullable=True) # Alias for market_key
    opening_line = Column(Float)
    opening_price = Column(Float)
    closing_line = Column(Float)
    closing_price = Column(Float)
    clv_beat = Column(Boolean)
    clv_percentage = Column(Float)
    clv_label = Column(String, nullable=True) # From analytical
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# --- LAYER 6: KALSHI ARB ---
class KalshiArbAlert(Base):
    __tablename__ = "kalshi_arb_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    event_name = Column(String)
    kalshi_price = Column(Float)
    bookie_price = Column(Float)
    bookmaker = Column(String)
    arb_percentage = Column(Float)
    is_live = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# --- LAYER 7: WEATHER/CONTEXT ---
class ConditionAlert(Base):
    __tablename__ = "conditions_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String, index=True)
    sport = Column(String)
    condition_type = Column(String) # 'weather', 'venue', 'travel'
    alert_text = Column(String)
    impact_score = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# --- LAYER 8: DIVERGENCE ---
class DivergenceSignal(Base):
    __tablename__ = "divergence_signals"
    
    id = Column(Integer, primary_key=True, index=True)
    sport = Column(String, index=True)
    event_id = Column(String, index=True)
    selection = Column(String)
    public_percent = Column(Float)
    line_movement = Column(String) # 'Fading Public', 'Follow Sharps'
    signal_strength = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class InferenceLog(Base):
    __tablename__ = "inference_logs"

    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String, nullable=True)
    input_summary = Column(String, nullable=True)
    output_summary = Column(String, nullable=True)
    confidence = Column(Float, nullable=True)
    sport = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class WhaleMove(Base):
    """
    Consolidated Sharp/Whale activity with before/after state.
    """
    __tablename__ = "whale_moves"
    __table_args__ = {"extend_existing": True}
    
    id = Column(Integer, primary_key=True, index=True)
    sport = Column(String, index=True)
    event_id = Column(String, index=True, nullable=True)
    player_name = Column(String, index=True, nullable=True) # From analytical
    market_key = Column(String, nullable=True)
    stat_type = Column(String, nullable=True) # From analytical
    selection = Column(String, nullable=True)
    bookmaker = Column(String, nullable=True)
    books_involved = Column(String, nullable=True) # From analytical
    price_before = Column(Float, nullable=True)
    price_after = Column(Float, nullable=True)
    line = Column(Float, nullable=True) # From analytical
    line_before = Column(Float, nullable=True)
    line_after = Column(Float, nullable=True)
    side = Column(String, nullable=True) # From analytical
    move_type = Column(String, nullable=True) # From analytical
    whale_rating = Column(Float, nullable=True) # 0-10 intensity
    whale_label = Column(String, nullable=True) # From analytical
    move_size = Column(String, nullable=True) # 'significant', 'wormhole', etc.
    amount_estimate = Column(Float, nullable=True) # From analytical
    severity = Column(String, nullable=True) # From analytical (string variant)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

class InjuryImpactEvent(Base):
    """
    Live player status changes and their quantified line impact.
    """
    __tablename__ = "injury_impact_events"
    
    id = Column(Integer, primary_key=True, index=True)
    sport = Column(String, index=True)
    event_id = Column(String, index=True)
    player_name = Column(String, index=True)
    status_before = Column(String) # 'healthy', 'questionable'
    status_after = Column(String)  # 'out', 'active'
    impact_score = Column(Float)   # Quantified line impact (e.g. -2.5 points)
    affected_markets = Column(JSON) # e.g. ['spread', 'total']
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

# --- MIGRATED FROM ANALYTICAL.PY ---

class SteamEvent(Base):
    __tablename__ = "steam_events"
    __table_args__ = {"extend_existing": True}
    
    id = Column(Integer, primary_key=True, index=True)
    sport = Column(String, index=True)
    player_name = Column(String, index=True)
    stat_type = Column(String)
    side = Column(String)
    line = Column(Float)
    movement = Column(Float)
    book_count = Column(Integer)
    severity = Column(Float)
    description = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class HitRateModel(Base):
    __tablename__ = "player_hit_rates"
    __table_args__ = {"extend_existing": True}
    
    id = Column(Integer, primary_key=True, index=True)
    player_name = Column(String, index=True)
    stat_type = Column(String, index=True) # e.g. 'points', 'rebounds'
    
    # Hit rates as percentages (0-100)
    l5_hit_rate = Column(Float, default=0.0)
    l10_hit_rate = Column(Float, default=0.0)
    l20_hit_rate = Column(Float, default=0.0)
    
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class PlayerStats(Base):
    """Historical player stats for H2H and Trend analysis"""
    __tablename__ = "player_stats_v2" # Using v2 to avoid conflicts with old stubs
    __table_args__ = {"extend_existing": True}
    
    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(String, index=True)
    player_name = Column(String, index=True)
    game_date = Column(DateTime(timezone=True), index=True)
    stat_category = Column(String, index=True) # e.g. 'points'
    value = Column(Float)
    opponent_team = Column(String)
    is_home = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

if hasattr(SQLModel, "metadata"):
    class NeuralEdge(SQLModel, table=True):
        __tablename__ = "edges_v2"
        id: Optional[int] = Field(default=None, primary_key=True)
        # Using String for foreign key if table not perfectly synced in metadata
        prop_id: int = Field(index=True) 
        ev: float = Field(index=True)  # expected value
        hit_rate: float = Field(index=True)  # % success
        model_confidence: float = Field(default=0.0)
        created_at: dt = Field(sa_column=SAColumn(DateTime(timezone=True), server_default=func.now()))
else:
    class NeuralEdge(Base):
        __tablename__ = "edges_v2"
        __table_args__ = {"extend_existing": True}
        id = Column(Integer, primary_key=True, index=True)
        prop_id = Column(Integer, index=True)
        ev = Column(Float, index=True)
        hit_rate = Column(Float, index=True)
        model_confidence = Column(Float, default=0.0)
        created_at = Column(DateTime(timezone=True), server_default=func.now())
