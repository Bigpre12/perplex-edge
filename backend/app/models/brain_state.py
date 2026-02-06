"""
Brain State Model - PostgreSQL persistence for autonomous brain operations.

Stores brain decisions, health checks, healing actions, and system state
in PostgreSQL for persistence across restarts and historical analysis.
"""

from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from sqlalchemy import Column, Integer, String, DateTime, JSON, Float, Boolean, Text, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import Base


class BrainDecision(Base):
    """Persisted brain decisions for historical tracking."""
    
    __tablename__ = "brain_decisions"
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    category = Column(String(50), nullable=False)  # "monitor", "heal", "optimize", "alert"
    action = Column(String(200), nullable=False)
    reasoning = Column(Text, nullable=False)
    outcome = Column(String(50), nullable=False)  # "success", "failed", "skipped"
    details = Column(JSON, default=dict)
    
    # Performance tracking
    duration_ms = Column(Integer, default=0)
    correlation_id = Column(String(100), nullable=True)  # For operation tracking
    
    # Indexes for queries
    __table_args__ = (
        Index('ix_brain_decisions_timestamp', 'timestamp'),
        Index('ix_brain_decisions_category', 'category'),
        Index('ix_brain_decisions_outcome', 'outcome'),
        Index('ix_brain_decisions_correlation', 'correlation_id'),
    )
    
    def __repr__(self) -> str:
        return f"<BrainDecision(id={self.id}, category={self.category}, action={self.action[:50]}, outcome={self.outcome})>"


class BrainHealthCheck(Base):
    """Persisted health checks for trend analysis."""
    
    __tablename__ = "brain_health_checks"
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    component = Column(String(100), nullable=False)
    status = Column(String(20), nullable=False)  # "healthy", "degraded", "critical"
    message = Column(Text, nullable=False)
    details = Column(JSON, default=dict)
    
    # Performance metrics
    response_time_ms = Column(Integer, default=0)
    error_count = Column(Integer, default=0)
    
    # Indexes
    __table_args__ = (
        Index('ix_brain_health_timestamp', 'timestamp'),
        Index('ix_brain_health_component', 'component'),
        Index('ix_brain_health_status', 'status'),
    )
    
    def __repr__(self) -> str:
        return f"<BrainHealthCheck(id={self.id}, component={self.component}, status={self.status})>"


class BrainHealingAction(Base):
    """Persisted healing actions for effectiveness tracking."""
    
    __tablename__ = "brain_healing_actions"
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    action = Column(String(200), nullable=False)
    target = Column(String(100), nullable=False)
    reason = Column(Text, nullable=False)
    result = Column(String(20), nullable=False)  # "success", "failed", "skipped"
    duration_ms = Column(Integer, default=0)
    details = Column(JSON, default=dict)
    
    # Success tracking
    success_rate = Column(Float, default=0.0)
    consecutive_failures = Column(Integer, default=0)
    
    # Indexes
    __table_args__ = (
        Index('ix_brain_healing_timestamp', 'timestamp'),
        Index('ix_brain_healing_action', 'action'),
        Index('ix_brain_healing_result', 'result'),
        Index('ix_brain_healing_target', 'target'),
    )
    
    def __repr__(self) -> str:
        return f"<BrainHealingAction(id={self.id}, action={self.action}, result={self.result})>"


class BrainSystemState(Base):
    """Persisted brain system state for recovery after restarts."""
    
    __tablename__ = "brain_system_state"
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    cycle_count = Column(Integer, default=0)
    overall_status = Column(String(20), default="initializing")
    
    # Healing statistics
    heals_attempted = Column(Integer, default=0)
    heals_succeeded = Column(Integer, default=0)
    consecutive_failures = Column(JSON, default=dict)
    
    # Optimization state
    sport_priority = Column(JSON, default=dict)
    quota_budget = Column(JSON, default=dict)
    
    # Auto-Git tracking
    auto_commit_enabled = Column(Boolean, default=True)
    git_commits_made = Column(Integer, default=0)
    
    # Betting Intelligence tracking
    betting_opportunities_found = Column(Integer, default=0)
    strong_bets_identified = Column(Integer, default=0)
    last_betting_scan = Column(DateTime(timezone=True), nullable=True)
    top_betting_opportunities = Column(JSON, default=list)
    
    # Performance metrics
    last_cycle_duration_ms = Column(Integer, default=0)
    uptime_hours = Column(Float, default=0.0)
    
    # Indexes
    __table_args__ = (
        Index('ix_brain_state_timestamp', 'timestamp'),
        Index('ix_brain_state_status', 'overall_status'),
    )
    
    def __repr__(self) -> str:
        return f"<BrainSystemState(id={self.id}, status={self.overall_status}, cycles={self.cycle_count})>"


class BrainAnomaly(Base):
    """Persisted anomalies detected by the brain."""
    
    __tablename__ = "brain_anomalies"
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    metric_name = Column(String(100), nullable=False)
    baseline_value = Column(Float, nullable=False)
    current_value = Column(Float, nullable=False)
    change_pct = Column(Float, nullable=False)
    severity = Column(String(20), nullable=False)  # "low", "medium", "high", "critical"
    status = Column(String(20), default="active")  # "active", "resolved", "ignored"
    details = Column(JSON, default=dict)
    
    # Resolution tracking
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    resolution_method = Column(String(100), nullable=True)
    
    # Indexes
    __table_args__ = (
        Index('ix_brain_anomalies_timestamp', 'timestamp'),
        Index('ix_brain_anomalies_metric', 'metric_name'),
        Index('ix_brain_anomalies_severity', 'severity'),
        Index('ix_brain_anomalies_status', 'status'),
    )
    
    def __repr__(self) -> str:
        return f"<BrainAnomaly(id={self.id}, metric={self.metric_name}, severity={self.severity})>"


class BrainBusinessMetrics(Base):
    """Persisted business metrics for trend analysis."""
    
    __tablename__ = "brain_business_metrics"
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    
    # Core metrics
    total_recommendations = Column(Integer, default=0)
    recommendation_hit_rate = Column(Float, default=0.0)
    average_ev = Column(Float, default=0.0)
    clv_trend = Column(Float, default=0.0)
    prop_volume = Column(Integer, default=0)
    user_confidence_score = Column(Float, default=0.0)
    
    # Performance metrics
    api_response_time_ms = Column(Float, default=0.0)
    error_rate = Column(Float, default=0.0)
    throughput = Column(Float, default=0.0)
    
    # System metrics
    cpu_usage = Column(Float, default=0.0)
    memory_usage = Column(Float, default=0.0)
    disk_usage = Column(Float, default=0.0)
    
    # Indexes
    __table_args__ = (
        Index('ix_brain_metrics_timestamp', 'timestamp'),
        Index('ix_brain_metrics_hit_rate', 'recommendation_hit_rate'),
        Index('ix_brain_metrics_ev', 'average_ev'),
    )
    
    def __repr__(self) -> str:
        return f"<BrainBusinessMetrics(id={self.id}, hit_rate={self.recommendation_hit_rate:.3f}, ev={self.average_ev:.3f})>"


class BrainCorrelation(Base):
    """Persisted correlation tracking for distributed operations."""
    
    __tablename__ = "brain_correlations"
    
    id = Column(Integer, primary_key=True)
    correlation_id = Column(String(100), nullable=False, unique=True)
    operation_type = Column(String(100), nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    completed_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(20), default="running")  # "running", "completed", "failed", "cancelled"
    duration_ms = Column(Integer, default=0)
    
    # Operation details
    details = Column(JSON, default=dict)
    result = Column(JSON, default=dict)
    error_message = Column(Text, nullable=True)
    
    # Event timeline (stored as JSON array)
    events = Column(JSON, default=list)
    
    # Indexes
    __table_args__ = (
        Index('ix_brain_correlations_id', 'correlation_id'),
        Index('ix_brain_correlations_type', 'operation_type'),
        Index('ix_brain_correlations_status', 'status'),
        Index('ix_brain_correlations_started', 'started_at'),
    )
    
    def __repr__(self) -> str:
        return f"<BrainCorrelation(id={self.id}, correlation_id={self.correlation_id}, status={self.status})>"


class BrainLearning(Base):
    """Persisted learning and adaptation data."""
    
    __tablename__ = "brain_learning"
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    learning_type = Column(String(50), nullable=False)  # "baseline_update", "pattern_recognition", "optimization"
    
    # Learning data
    metric_name = Column(String(100), nullable=False)
    old_value = Column(Float, nullable=False)
    new_value = Column(Float, nullable=False)
    confidence = Column(Float, default=0.0)
    
    # Context
    context = Column(JSON, default=dict)
    impact_assessment = Column(JSON, default=dict)
    
    # Validation
    validated_at = Column(DateTime(timezone=True), nullable=True)
    validation_result = Column(String(20), nullable=True)  # "confirmed", "rejected", "pending"
    
    # Indexes
    __table_args__ = (
        Index('ix_brain_learning_timestamp', 'timestamp'),
        Index('ix_brain_learning_type', 'learning_type'),
        Index('ix_brain_learning_metric', 'metric_name'),
    )
    
    def __repr__(self) -> str:
        return f"<BrainLearning(id={self.id}, type={self.learning_type}, metric={self.metric_name})>"
