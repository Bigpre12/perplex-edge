from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, JSON, BigInteger, Numeric, UniqueConstraint, Index, Column as SAColumn
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
    
    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(String, index=True)
    player_name = Column(String, index=True)
    game_date = Column(DateTime(timezone=True), index=True)
    stat_category = Column(String, index=True) # e.g. 'points'
    value = Column(Float)
    opponent_team = Column(String)
    is_home = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class NeuralEdge(Base):
    __tablename__ = "edges_v2"
    id = Column(Integer, primary_key=True, index=True)
    prop_id = Column(Integer, index=True)
    ev = Column(Float, index=True)
    hit_rate = Column(Float, index=True)
    model_confidence = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# --- MIGRATED FROM REFEREES.PY ---
class RefereeGame(Base):
    __tablename__ = "refereegames"
    id = Column(Integer, primary_key=True, index=True)
    ref_name = Column(String, index=True)
    game_id = Column(String, index=True)
    total_fouls = Column(Integer, default=0)
    pace = Column(Float, default=0.0)
    total_points = Column(Integer, default=0)
    fta = Column(Integer, default=0) # Free Throw Attempts
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# --- MIGRATED FROM SCHEDULE.PY ---
class Schedule(Base):
    __tablename__ = "schedules"
    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(String, unique=True, index=True)
    sport = Column(String)
    home_team = Column(String)
    away_team = Column(String)
    commence_time = Column(DateTime(timezone=True))
    referee_crew = Column(String, nullable=True) # Sprint 17: Comma-separated crew names
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# --- MIGRATED FROM SIGNALS.PY ---
class Signal(Base):
    """Sharp, Steam, Whale, and RLM signals."""
    __tablename__ = "signals"
    id = Column(BigInteger, primary_key=True)
    sport = Column(String, nullable=False, index=True)
    event_id = Column(String, nullable=False, index=True)
    signal_type = Column(String, nullable=False, index=True)  # 'steam', 'sharp', 'whale', 'rlm', 'clv'
    market_key = Column(String, nullable=False)
    outcome_key = Column(String, nullable=False)
    player_name = Column(String, nullable=True, index=True)
    book_origin = Column(String, nullable=True)
    line_open = Column(Numeric, nullable=True)
    line_current = Column(Numeric, nullable=True)
    line_delta = Column(Numeric, nullable=True)
    sharp_pct = Column(Numeric, nullable=True)
    public_pct = Column(Numeric, nullable=True)
    confidence = Column(Numeric, nullable=True)
    detail = Column(JSON, nullable=True)
    detected_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)

class InjuryImpact(Base):
    """Quantified impact of player injuries."""
    __tablename__ = "injury_impacts"
    id = Column(BigInteger, primary_key=True)
    sport = Column(String, index=True)
    player_name = Column(String, index=True)
    team = Column(String)
    status = Column(String) # 'Out', 'Questionable'
    impact_description = Column(String)
    affected_markets = Column(JSON) # e.g. [{"market": "points", "adjustment": -2.5}]
    teammate_boosts = Column(JSON) # e.g. [{"player": "Teammate A", "boost": 0.15}]
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class LinePrediction(Base):
    """Predicted line movements."""
    __tablename__ = "line_predictions"
    id = Column(BigInteger, primary_key=True)
    sport = Column(String, index=True)
    event_id = Column(String, index=True)
    market_key = Column(String)
    current_line = Column(Numeric)
    predicted_line = Column(Numeric)
    confidence = Column(Numeric)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# --- MIGRATED FROM UNIFIED.PY ---
class UnifiedOdds(Base):
    """
    Unified odds snapshot used by SharpMoneyBrain and CLV tracker.
    Source of truth should be your odds ingestion (props + game lines)
    writing into this table or a view.
    """
    __tablename__ = "unified_odds"

    id = Column(Integer, primary_key=True, index=True)
    sport = Column(String, index=True)
    event_id = Column(String, index=True)        # game id or event id
    market_key = Column(String, index=True)      # e.g. 'player_points'
    outcome_key = Column(String, index=True)     # e.g. 'LeBron_over_27.5'
    bookmaker = Column(String, index=True)

    line = Column(Float, nullable=True)          # numeric line if applicable
    price = Column(Float, nullable=False)        # decimal odds (not American)
    implied_prob = Column(Float, nullable=True)   # percentage (0-1)
    player_name = Column(String, index=True, nullable=True)
    league = Column(String, nullable=True)
    game_time = Column(DateTime(timezone=True), nullable=True)
    home_team = Column(String, nullable=True)
    away_team = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    __table_args__ = (UniqueConstraint('sport', 'event_id', 'player_name', 'market_key', 'outcome_key', 'bookmaker', name='uix_unified_odds_unique'),)

class UnifiedEVSignal(Base):
    """Unified EV Signals: Computed betting edges from the EV engine."""
    __tablename__ = "ev_signals"
    id = Column(Integer, primary_key=True, autoincrement=True)
    sport = Column(String, nullable=False, index=True)
    sport_key = Column(String, nullable=True) # Compatibility
    prop_type = Column(String, nullable=True, index=True) # e.g. 'Player Points'
    event_id = Column(String, nullable=False, index=True)
    market_key = Column(String, nullable=False, index=True)
    outcome_key = Column(String, nullable=True) # can be 'over'/'under' or side name
    player_name = Column(String, nullable=True, index=True)
    bookmaker = Column(String, nullable=False, index=True)
    price = Column(Float, nullable=False)
    line = Column(Float, nullable=True)
    confidence = Column(Float, nullable=True)
    
    # Extended Schema (New)
    true_prob = Column(Float, nullable=True)
    edge_percent = Column(Float, nullable=True)
    implied_prob = Column(Float, nullable=True)
    
    # Legacy/Rich Schema Compatibility
    ev_score = Column(Float, nullable=True)     # Often same as edge_percent/100
    ev_percent = Column(Float, nullable=True)   # Often same as edge_percent
    ev_percentage = Column(Float, nullable=True) # Frontend expected name
    fair_prob = Column(Float, nullable=True)    # Alias for true_prob
    market_prob = Column(Float, nullable=True)  # Alias for implied_prob
    recommendation = Column(String, nullable=True) # 'OVER'/'UNDER'
    
    engine_version = Column(String, nullable=False, server_default='v1')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), index=True)
    
    __table_args__ = (
        UniqueConstraint('sport', 'event_id', 'player_name', 'market_key', 'outcome_key', 'bookmaker', 'engine_version', name='uix_ev_unique'),
        Index('idx_ev_signals_player_market', 'player_name', 'market_key'),
    )

class LineTick(Base):
    """Line Ticks: Historical record of price/line changes for movement analysis."""
    __tablename__ = "line_ticks"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    sport = Column(String, nullable=False, index=True)
    event_id = Column(String, nullable=False, index=True)
    market_key = Column(String, nullable=False, index=True)
    outcome_key = Column(String, nullable=False)
    player_name = Column(String, nullable=True, index=True)
    bookmaker = Column(String, nullable=False, index=True)
    price = Column(Numeric, nullable=False)
    line = Column(Numeric, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

class UnifiedEVSignalHistory(Base):
    """Historical record of EV signals for trend analysis."""
    __tablename__ = "ev_signals_history"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    sport = Column(String, nullable=False, index=True)
    event_id = Column(String, nullable=False, index=True)
    market_key = Column(String, nullable=False, index=True)
    outcome_key = Column(String, nullable=False)
    player_name = Column(String, nullable=True)
    bookmaker = Column(String, nullable=False, index=True)
    price = Column(Numeric, nullable=False)
    line = Column(Numeric, nullable=True)
    edge_percent = Column(Numeric, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

class PropLive(Base):
    """Market-based live props (Over/Under consolidated)."""
    __tablename__ = "props_live"
    id = Column(Integer, primary_key=True, autoincrement=True)
    sport = Column(String, nullable=False, index=True)
    league = Column(String, nullable=True)
    game_id = Column(String, nullable=False, index=True)
    game_start_time = Column(DateTime(timezone=True), nullable=True)
    player_id = Column(String, nullable=True, index=True)
    player_name = Column(String, nullable=True, index=True)
    team = Column(String, nullable=True)
    market_key = Column(String, nullable=False, index=True)
    market_label = Column(String, nullable=True)
    line = Column(Numeric, nullable=True)
    book = Column(String, nullable=False, index=True)
    odds_over = Column(Numeric, nullable=True)
    odds_under = Column(Numeric, nullable=True)
    implied_over = Column(Numeric, nullable=True)
    implied_under = Column(Numeric, nullable=True)
    source_ts = Column(DateTime(timezone=True), nullable=True)
    ingested_ts = Column(DateTime(timezone=True), nullable=True)
    is_best_over = Column(Boolean, default=False)
    is_best_under = Column(Boolean, default=False)
    is_soft_book = Column(Boolean, default=False)
    is_sharp_book = Column(Boolean, default=False)
    confidence = Column(Float, nullable=True) # 0.0 to 1.0
    evpercentage = Column(Float, default=0.0) # For grading
    last_updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    home_team = Column(String, nullable=True)
    away_team = Column(String, nullable=True)
    # Note: We manage unique indexes manually in main.py to be robust across environments
    __table_args__ = (
        Index('idx_props_live_sport_game', 'sport', 'game_id'),
    )

class PropHistory(Base):
    """Historical record of prop snapshots (Over/Under consolidated)."""
    __tablename__ = "props_history"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    snapshot_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    sport = Column(String, nullable=False, index=True)
    league = Column(String, nullable=True)
    game_id = Column(String, nullable=False, index=True)
    game_start_time = Column(DateTime(timezone=True), nullable=True)
    player_id = Column(String, nullable=True, index=True)
    player_name = Column(String, nullable=True, index=True)
    team = Column(String, nullable=True)
    market_key = Column(String, nullable=False, index=True)
    market_label = Column(String, nullable=True)
    line = Column(Numeric, nullable=True)
    book = Column(String, nullable=False, index=True)
    odds_over = Column(Numeric, nullable=True)
    odds_under = Column(Numeric, nullable=True)
    implied_over = Column(Numeric, nullable=True)
    implied_under = Column(Numeric, nullable=True)
    source_ts = Column(DateTime(timezone=True), nullable=True)
    ingested_ts = Column(DateTime(timezone=True), nullable=True)
    source = Column(String, nullable=True)
    run_id = Column(String, nullable=True)
    home_team = Column(String, nullable=True)
    away_team = Column(String, nullable=True)
    is_close = Column(Boolean, default=False)
    is_best_over = Column(Boolean, default=False)
    is_best_under = Column(Boolean, default=False)
    is_soft_book = Column(Boolean, default=False)
    is_sharp_book = Column(Boolean, default=False)
    confidence = Column(Float, nullable=True)

class EdgeEVHistory(Base):
    """Historical record of EV edges found by the brain."""
    __tablename__ = "edges_ev_history"
    id = Column(Integer, primary_key=True, autoincrement=True)
    sport = Column(String, nullable=False, index=True)
    league = Column(String, nullable=True)
    game_id = Column(String, nullable=False, index=True)
    game_start_time = Column(DateTime(timezone=True), nullable=True)
    player_id = Column(String, nullable=True, index=True)
    player_name = Column(String, nullable=True, index=True)
    team = Column(String, nullable=True)
    market_key = Column(String, nullable=False, index=True)
    market_label = Column(String, nullable=True)
    line = Column(Numeric, nullable=False)
    book = Column(String, nullable=False, index=True)
    side = Column(String, nullable=False) # 'over', 'under', 'home', etc.
    odds = Column(Numeric, nullable=False)
    model_prob = Column(Numeric, nullable=True)
    implied_prob = Column(Numeric, nullable=False)
    edge_pct = Column(Numeric, nullable=False)
    snapshot_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    source = Column(String, nullable=True)
    run_id = Column(String, nullable=True)
