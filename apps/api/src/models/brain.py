from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, JSON
from sqlalchemy.sql import func
from db.base import Base

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
    
    id = Column(Integer, primary_key=True, index=True)
    sport = Column(String, index=True)
    event_id = Column(String, index=True)
    market_key = Column(String)
    selection = Column(String)
    opening_line = Column(Float)
    opening_price = Column(Float)
    closing_line = Column(Float)
    closing_price = Column(Float)
    clv_beat = Column(Boolean)
    clv_percentage = Column(Float)
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
