"""
Brain service configuration management and policy layer.
Centralizes strategy configuration, thresholds, and operational policies.
"""

import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class StrategyConfig:
    """Configuration for a specific brain strategy."""
    name: str
    description: str
    enabled: bool
    priority: int  # Lower number = higher priority
    parameters: Dict[str, Any]
    conditions: List[str]  # When this strategy applies
    limits: Dict[str, Any]  # Safety limits
    
@dataclass
class ThresholdConfig:
    """Threshold configuration for metrics and alerts."""
    metric_name: str
    target_value: float
    warning_threshold: float
    critical_threshold: float
    adaptive: bool = False  # Whether threshold adapts over time
    adaptation_rate: float = 0.1  # Rate of adaptation
    
@dataclass
class ExplorationConfig:
    """Configuration for multi-armed bandit exploration."""
    strategy_name: str
    exploration_rate: float  # 0.0 = pure exploitation, 1.0 = pure exploration
    min_exploration_rate: float = 0.05
    max_exploration_rate: float = 0.3
    adaptation_enabled: bool = True
    performance_window_days: int = 7

@dataclass
class BaselineConfig:
    """Configuration for metric baselines."""
    metric_name: str
    baseline_type: str  # "static", "adaptive", "seasonal"
    initial_value: float
    update_frequency_hours: int
    freeze_conditions: List[str]  # When to freeze baseline
    reset_conditions: List[str]   # When to reset baseline

class BrainConfigManager:
    """Manages brain service configuration with dynamic updates."""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or "brain_config.json"
        self.strategies: Dict[str, StrategyConfig] = {}
        self.thresholds: Dict[str, ThresholdConfig] = {}
        self.exploration_configs: Dict[str, ExplorationConfig] = {}
        self.baseline_configs: Dict[str, BaselineConfig] = {}
        self.policies: Dict[str, Any] = {}
        self.last_updated = datetime.now(timezone.utc)
        
        self._load_default_config()
    
    def _load_default_config(self):
        """Load default configuration."""
        # Default strategies
        self.strategies = {
            "aggressive_healing": StrategyConfig(
                name="aggressive_healing",
                description="Aggressive healing with higher risk tolerance",
                enabled=False,
                priority=2,
                parameters={
                    "max_data_deletion_mb": 200.0,
                    "auto_approval_enabled": True,
                    "heal_timeout_minutes": 5
                },
                conditions=["system_health_critical", "storage_low"],
                limits={
                    "max_deletes_per_hour": 1000,
                    "max_config_changes_per_day": 10
                }
            ),
            
            "conservative_healing": StrategyConfig(
                name="conservative_healing",
                description="Conservative healing with manual approval required",
                enabled=True,
                priority=1,
                parameters={
                    "max_data_deletion_mb": 50.0,
                    "auto_approval_enabled": False,
                    "heal_timeout_minutes": 15
                },
                conditions=["data_quality_degraded", "performance_issues"],
                limits={
                    "max_deletes_per_hour": 100,
                    "max_config_changes_per_day": 2
                }
            ),
            
            "business_metric_optimization": StrategyConfig(
                name="business_metric_optimization",
                description="Optimize business metrics with careful monitoring",
                enabled=True,
                priority=3,
                parameters={
                    "ev_optimization_enabled": True,
                    "hit_rate_optimization_enabled": True,
                    "prop_volume_optimization_enabled": False
                },
                conditions=["business_metrics_degraded"],
                limits={
                    "max_threshold_change_pct": 0.1,
                    "max_sports_changed_per_day": 1
                }
            )
        }
        
        # Default thresholds
        self.thresholds = {
            "hit_rate": ThresholdConfig(
                metric_name="hit_rate",
                target_value=0.55,
                warning_threshold=0.45,
                critical_threshold=0.30,
                adaptive=True,
                adaptation_rate=0.05
            ),
            
            "average_ev": ThresholdConfig(
                metric_name="average_ev",
                target_value=0.05,
                warning_threshold=0.01,
                critical_threshold=-0.01,
                adaptive=True,
                adaptation_rate=0.02
            ),
            
            "data_quality_score": ThresholdConfig(
                metric_name="data_quality_score",
                target_value=0.95,
                warning_threshold=0.85,
                critical_threshold=0.70,
                adaptive=False
            ),
            
            "heal_success_rate": ThresholdConfig(
                metric_name="heal_success_rate",
                target_value=0.90,
                warning_threshold=0.75,
                critical_threshold=0.50,
                adaptive=False
            )
        }
        
        # Default exploration configs
        self.exploration_configs = {
            "sync_frequency": ExplorationConfig(
                strategy_name="sync_frequency",
                exploration_rate=0.1,
                adaptation_enabled=True,
                performance_window_days=7
            ),
            
            "sport_prioritization": ExplorationConfig(
                strategy_name="sport_prioritization",
                exploration_rate=0.05,
                adaptation_enabled=True,
                performance_window_days=14
            ),
            
            "api_quota_allocation": ExplorationConfig(
                strategy_name="api_quota_allocation",
                exploration_rate=0.15,
                adaptation_enabled=True,
                performance_window_days=3
            )
        }
        
        # Default baseline configs
        self.baseline_configs = {
            "api_response_time": BaselineConfig(
                metric_name="api_response_time",
                baseline_type="adaptive",
                initial_value=1000.0,
                update_frequency_hours=1,
                freeze_conditions=["system_under_load", "api_degraded"],
                reset_conditions=["api_provider_changed", "major_system_update"]
            ),
            
            "prop_volume": BaselineConfig(
                metric_name="prop_volume",
                baseline_type="seasonal",
                initial_value=1000.0,
                update_frequency_hours=6,
                freeze_conditions=["playoffs", "major_events"],
                reset_conditions=["season_start", "rule_changes"]
            ),
            
            "error_rate": BaselineConfig(
                metric_name="error_rate",
                baseline_type="adaptive",
                initial_value=0.01,
                update_frequency_hours=2,
                freeze_conditions=["system_maintenance", "feature_rollout"],
                reset_conditions=["major_incident", "architecture_change"]
            )
        }
        
        # Default policies
        self.policies = {
            "quiet_hours": {
                "weekdays": ["01:00-06:00"],
                "weekends": ["02:00-07:00"],
                "holidays": True
            },
            
            "approval_policies": {
                "auto_approved_actions": [
                    "cache_clearing",
                    "log_rotation",
                    "temporary_file_cleanup",
                    "baseline_adjustment"
                ],
                "manual_approval_required": [
                    "critical_data_deletion",
                    "sport_disable",
                    "model_retraining",
                    "ev_threshold_change",
                    "hit_rate_threshold_change"
                ],
                "approval_timeout_minutes": 30
            },
            
            "exploration_policies": {
                "max_exploration_rate": 0.3,
                "min_confidence_samples": 50,
                "exploration_budget_daily": 100,
                "risk_tolerance_level": "medium"
            },
            
            "baseline_policies": {
                "max_adaptation_rate": 0.2,
                "baseline_retention_days": 90,
                "freeze_duration_hours": 24,
                "reset_confirmation_required": True
            }
        }
    
    def get_strategy(self, name: str) -> Optional[StrategyConfig]:
        """Get a strategy configuration by name."""
        return self.strategies.get(name)
    
    def get_enabled_strategies(self) -> List[StrategyConfig]:
        """Get all enabled strategies sorted by priority."""
        enabled = [s for s in self.strategies.values() if s.enabled]
        return sorted(enabled, key=lambda x: x.priority)
    
    def get_threshold(self, metric_name: str) -> Optional[ThresholdConfig]:
        """Get threshold configuration for a metric."""
        return self.thresholds.get(metric_name)
    
    def update_threshold(self, metric_name: str, new_value: float, adaptive: bool = False):
        """Update a threshold value."""
        if metric_name in self.thresholds:
            threshold = self.thresholds[metric_name]
            if adaptive and threshold.adaptive:
                # Gradual adaptation
                threshold.target_value = (
                    threshold.target_value * (1 - threshold.adaptation_rate) + 
                    new_value * threshold.adaptation_rate
                )
            else:
                threshold.target_value = new_value
            
            self.last_updated = datetime.now(timezone.utc)
            logger.info(f"[CONFIG] Updated threshold {metric_name}: {threshold.target_value}")
    
    def get_exploration_config(self, strategy_name: str) -> Optional[ExplorationConfig]:
        """Get exploration configuration for a strategy."""
        return self.exploration_configs.get(strategy_name)
    
    def update_exploration_rate(self, strategy_name: str, performance_score: float):
        """Update exploration rate based on performance."""
        config = self.get_exploration_config(strategy_name)
        if config and config.adaptation_enabled:
            # Higher performance = less exploration, lower performance = more exploration
            if performance_score > 0.7:  # Good performance
                config.exploration_rate = max(
                    config.min_exploration_rate,
                    config.exploration_rate * 0.9
                )
            elif performance_score < 0.4:  # Poor performance
                config.exploration_rate = min(
                    config.max_exploration_rate,
                    config.exploration_rate * 1.1
                )
            
            self.last_updated = datetime.now(timezone.utc)
            logger.info(f"[CONFIG] Updated exploration rate for {strategy_name}: {config.exploration_rate:.3f}")
    
    def get_baseline_config(self, metric_name: str) -> Optional[BaselineConfig]:
        """Get baseline configuration for a metric."""
        return self.baseline_configs.get(metric_name)
    
    def should_freeze_baseline(self, metric_name: str, current_conditions: List[str]) -> bool:
        """Check if baseline should be frozen based on conditions."""
        config = self.get_baseline_config(metric_name)
        if not config:
            return False
        
        return any(condition in current_conditions for condition in config.freeze_conditions)
    
    def should_reset_baseline(self, metric_name: str, current_conditions: List[str]) -> bool:
        """Check if baseline should be reset based on conditions."""
        config = self.get_baseline_config(metric_name)
        if not config:
            return False
        
        return any(condition in current_conditions for condition in config.reset_conditions)
    
    def evaluate_policy_compliance(self, action_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate if an action complies with current policies."""
        compliance = {
            "allowed": True,
            "requires_approval": False,
            "restrictions": [],
            "conditions": []
        }
        
        # Check approval policies
        if action_type in self.policies["approval_policies"]["manual_approval_required"]:
            compliance["requires_approval"] = True
            compliance["restrictions"].append("Manual approval required")
        
        # Check quiet hours
        current_hour = datetime.now().hour
        quiet_hours = self.policies["quiet_hours"]["weekdays"]
        
        for quiet_range in quiet_hours:
            start, end = map(int, quiet_range.split("-"))
            if start <= current_hour < end:
                compliance["conditions"].append(f"Quiet hours active ({quiet_range})")
                break
        
        # Check exploration policies
        if "exploration" in action_type.lower():
            max_rate = self.policies["exploration_policies"]["max_exploration_rate"]
            current_rate = context.get("exploration_rate", 0.1)
            if current_rate > max_rate:
                compliance["allowed"] = False
                compliance["restrictions"].append(f"Exploration rate {current_rate} exceeds max {max_rate}")
        
        return compliance
    
    def enable_strategy(self, name: str, reason: str = ""):
        """Enable a strategy."""
        if name in self.strategies:
            self.strategies[name].enabled = True
            self.last_updated = datetime.now(timezone.utc)
            logger.info(f"[CONFIG] Enabled strategy: {name} - {reason}")
    
    def disable_strategy(self, name: str, reason: str = ""):
        """Disable a strategy."""
        if name in self.strategies:
            self.strategies[name].enabled = False
            self.last_updated = datetime.now(timezone.utc)
            logger.info(f"[CONFIG] Disabled strategy: {name} - {reason}")
    
    def save_config(self):
        """Save current configuration to file."""
        try:
            config_data = {
                "strategies": {name: asdict(config) for name, config in self.strategies.items()},
                "thresholds": {name: asdict(config) for name, config in self.thresholds.items()},
                "exploration_configs": {name: asdict(config) for name, config in self.exploration_configs.items()},
                "baseline_configs": {name: asdict(config) for name, config in self.baseline_configs.items()},
                "policies": self.policies,
                "last_updated": self.last_updated.isoformat()
            }
            
            with open(self.config_file, 'w') as f:
                json.dump(config_data, f, indent=2, default=str)
            
            logger.info(f"[CONFIG] Saved configuration to {self.config_file}")
            
        except Exception as e:
            logger.error(f"[CONFIG] Failed to save configuration: {e}")
    
    def load_config(self):
        """Load configuration from file."""
        try:
            with open(self.config_file, 'r') as f:
                config_data = json.load(f)
            
            # Restore configurations
            for name, data in config_data.get("strategies", {}).items():
                self.strategies[name] = StrategyConfig(**data)
            
            for name, data in config_data.get("thresholds", {}).items():
                self.thresholds[name] = ThresholdConfig(**data)
            
            for name, data in config_data.get("exploration_configs", {}).items():
                self.exploration_configs[name] = ExplorationConfig(**data)
            
            for name, data in config_data.get("baseline_configs", {}).items():
                self.baseline_configs[name] = BaselineConfig(**data)
            
            self.policies = config_data.get("policies", {})
            
            if "last_updated" in config_data:
                self.last_updated = datetime.fromisoformat(config_data["last_updated"])
            
            logger.info(f"[CONFIG] Loaded configuration from {self.config_file}")
            
        except FileNotFoundError:
            logger.info(f"[CONFIG] Config file {self.config_file} not found, using defaults")
        except Exception as e:
            logger.error(f"[CONFIG] Failed to load configuration: {e}")
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get summary of current configuration."""
        return {
            "enabled_strategies": len([s for s in self.strategies.values() if s.enabled]),
            "total_strategies": len(self.strategies),
            "adaptive_thresholds": len([t for t in self.thresholds.values() if t.adaptive]),
            "total_thresholds": len(self.thresholds),
            "exploration_configs": len(self.exploration_configs),
            "baseline_configs": len(self.baseline_configs),
            "last_updated": self.last_updated.isoformat(),
            "policy_count": len(self.policies)
        }

# Global configuration manager
brain_config = BrainConfigManager()
