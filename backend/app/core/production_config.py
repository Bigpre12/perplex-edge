"""
Production configuration for brain service operations.
Defines alerting policies, runbooks, and governance rules.
"""

from datetime import time, datetime, timezone
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

class AlertSeverity(Enum):
    CRITICAL = "critical"  # Immediate human intervention required
    HIGH = "high"        # Human intervention within 30 minutes
    MEDIUM = "medium"    # Human intervention within 2 hours
    LOW = "low"          # Log only, no human intervention

class AlertCategory(Enum):
    BETTING_IMPACTING = "betting_impacting"  # Affects user bets/profitability
    DATA_INTEGRITY = "data_integrity"      # Bad data reaching users
    SYSTEM_HEALTH = "system_health"        # Infrastructure issues
    PERFORMANCE = "performance"            # Slow operations, high latency
    BUSINESS_METRICS = "business_metrics"    # Hit rate drops, EV issues

@dataclass
class AlertRule:
    """Defines when and how to alert on specific conditions."""
    name: str
    category: AlertCategory
    severity: AlertSeverity
    condition: str  # Metric condition that triggers alert
    threshold: float
    description: str
    runbook_id: Optional[str] = None
    quiet_hours: List[str] = None  # Hours when not to alert (24-hour format)
    escalation_hours: int = 2  # Hours before escalation
    auto_resolve: bool = False  # Auto-resolve if condition clears

@dataclass
class Runbook:
    """Step-by-step guide for handling specific alert types."""
    id: str
    title: str
    category: AlertCategory
    severity: AlertSeverity
    steps: List[str]
    checks: List[str]
    fix_actions: List[str]
    rollback_actions: List[str]
    escalation_triggers: List[str]
    estimated_time_minutes: int
    required_permissions: List[str]

@dataclass
class Guardrail:
    """Safety limits for automated healing actions."""
    name: str
    max_data_deletion_per_cycle_mb: float
    max_api_calls_per_hour: int
    max_config_changes_per_day: int
    safe_mode_enabled: bool
    requires_approval_for: List[str]
    explainability_required: bool = True

@dataclass
class MetricDefinition:
    """SLI-like metric definitions for production monitoring."""
    name: str
    description: str
    unit: str
    target_value: float
    warning_threshold: float
    critical_threshold: float
    category: str
    sli: bool = False  # Service Level Indicator

class ProductionConfig:
    """Production-ready configuration for brain service."""
    
    def __init__(self):
        self.alert_rules = self._define_alert_rules()
        self.runbooks = self._define_runbooks()
        self.guardrails = self._define_guardrails()
        self.metrics = self._define_metrics()
        self.policies = self._define_policies()
        self.deployment_checklist = self._define_deployment_checklist()
    
    def _define_alert_rules(self) -> List[AlertRule]:
        """Define when to trigger alerts."""
        return [
            # Critical alerts - immediate intervention
            AlertRule(
                name="hit_rate_crash",
                category=AlertCategory.BETTING_IMPACTING,
                severity=AlertSeverity.CRITICAL,
                condition="recommendation_hit_rate < 0.30",
                threshold=0.30,
                description="Recommendation hit rate dropped below 30%",
                runbook_id="hit_rate_crash",
                quiet_hours=["02:00-06:00"],  # Quiet hours
                escalation_hours=1,
                auto_resolve=False
            ),
            
            AlertRule(
                name="critical_data_quality",
                category=AlertCategory.DATA_INTEGRITY,
                severity=AlertSeverity.CRITICAL,
                condition="critical_data_quality_issues > 10",
                threshold=10,
                description="More than 10 critical data quality issues detected",
                runbook_id="data_quality_critical",
                escalation_hours=1,
                auto_resolve=False
            ),
            
            AlertRule(
                name="storage_exhaustion",
                category=AlertCategory.SYSTEM_HEALTH,
                severity=AlertSeverity.CRITICAL,
                condition="free_space_gb < 0.5",
                threshold=0.5,
                description="Storage critically low - system may fail",
                runbook_id="storage_critical",
                escalation_hours=0.5,
                auto_resolve=False
            ),
            
            # High priority alerts
            AlertRule(
                name="ev_performance_decline",
                category=AlertCategory.BUSINESS_METRICS,
                severity=AlertSeverity.HIGH,
                condition="average_ev < 0.01",
                threshold=0.01,
                description="Average EV dropped below 1%",
                runbook_id="ev_decline",
                quiet_hours=["01:00-05:00"],
                escalation_hours=2,
                auto_resolve=False
            ),
            
            AlertRule(
                name="api_response_degradation",
                category=AlertCategory.PERFORMANCE,
                severity=AlertSeverity.HIGH,
                condition="api_response_time_p95 > 5000",
                threshold=5000,
                description="API response time degraded significantly",
                runbook_id="api_slow",
                escalation_hours=2,
                auto_resolve=True
            ),
            
            # Medium priority alerts
            AlertRule(
                name="prop_volume_anomaly",
                category=AlertCategory.BUSINESS_METRICS,
                severity=AlertSeverity.MEDIUM,
                condition="prop_volume_change_pct > 0.50",
                threshold=0.50,
                description="Prop volume changed by more than 50%",
                runbook_id="prop_volume_anomaly",
                escalation_hours=4,
                auto_resolve=True
            ),
            
            AlertRule(
                name="data_quality_degraded",
                category=AlertCategory.DATA_INTEGRITY,
                severity=AlertSeverity.MEDIUM,
                condition="total_data_quality_issues > 25",
                threshold=25,
                description="Data quality degraded - multiple issues detected",
                runbook_id="data_quality_degraded",
                escalation_hours=4,
                auto_resolve=True
            ),
            
            # Low priority alerts
            AlertRule(
                name="heal_action_failure",
                category=AlertCategory.SYSTEM_HEALTH,
                severity=AlertSeverity.LOW,
                condition="heal_failure_rate > 0.5",
                threshold=0.5,
                description="High failure rate in heal actions",
                runbook_id="heal_failure",
                escalation_hours=8,
                auto_resolve=True
            ),
        ]
    
    def _define_runbooks(self) -> List[Runbook]:
        """Define step-by-step runbooks for common issues."""
        return [
            Runbook(
                id="hit_rate_crash",
                title="Hit Rate Crash Response",
                category=AlertCategory.BETTING_IMPACTING,
                severity=AlertSeverity.CRITICAL,
                steps=[
                    "1. Verify hit rate calculation accuracy",
                    "2. Check recent data quality issues",
                    "3. Review model probability calibration",
                    "4. Examine API data freshness",
                    "5. Check for market changes"
                ],
                checks=[
                    "SELECT COUNT(*) FROM model_picks WHERE created_at > NOW() - INTERVAL '1 hour'",
                    "SELECT AVG(model_probability) FROM model_picks WHERE created_at > NOW() - INTERVAL '1 hour'",
                    "SELECT COUNT(*) FROM model_picks WHERE expected_value < -0.1"
                ],
                fix_actions=[
                    "Disable affected sport recommendations",
                    "Clear corrupted data if identified",
                    "Re-run model calibration",
                    "Update model probability thresholds"
                ],
                rollback_actions=[
                    "Restore from backup if available",
                    "Revert model configuration changes",
                    "Disable new features temporarily"
                ],
                escalation_triggers=[
                    "Hit rate < 0.20 for more than 2 hours",
                    "Multiple sports affected simultaneously",
                    "User complaints received"
                ],
                estimated_time_minutes=30,
                required_permissions=["admin", "model_ops"]
            ),
            
            Runbook(
                id="data_quality_critical",
                title="Critical Data Quality Issues",
                category=AlertCategory.DATA_INTEGRITY,
                severity=AlertSeverity.CRITICAL,
                steps=[
                    "1. Identify problematic data sources",
                    "2. Quarantine affected data",
                    "3. Validate data source integrity",
                    "4. Clean or replace corrupted data",
                    "5. Update data validation rules"
                ],
                checks=[
                    "SELECT COUNT(*) FROM model_picks WHERE odds < -10000 OR odds > 10000",
                    "SELECT COUNT(*) FROM model_picks WHERE line_value < -100 OR line_value > 100",
                    "SELECT COUNT(*) FROM model_picks WHERE model_probability < 0 OR model_probability > 1"
                ],
                fix_actions=[
                    "Delete impossible odds/lines data",
                    "Mark suspicious records for review",
                    "Update validation rules",
                    "Implement source data validation"
                ],
                rollback_actions=[
                    "Restore from data backup",
                    "Undo bulk delete operations",
                    "Revert validation rule changes"
                ],
                escalation_triggers=[
                    "Data quality issues persist after cleanup",
                    "Multiple data sources affected",
                    "User-facing errors detected"
                ],
                estimated_time_minutes=45,
                required_permissions=["admin", "data_ops"]
            ),
            
            Runbook(
                id="storage_critical",
                title="Critical Storage Issues",
                category=AlertCategory.SYSTEM_HEALTH,
                severity=AlertSeverity.CRITICAL,
                steps=[
                    "1. Check current storage usage",
                    "2. Identify large files/directories",
                    "3. Clear temporary files and caches",
                    "4. Archive old logs",
                    "5. Monitor storage recovery"
                ],
                checks=[
                    "df -h /",
                    "du -sh /app/* | sort -hr | head -10",
                    "ls -la /tmp/ | wc -l",
                    "ls -la /app/logs/ | wc -l"
                ],
                fix_actions=[
                    "Clear /tmp directory",
                    "Rotate large log files",
                    "Clear application cache",
                    "Remove temporary files"
                ],
                rollback_actions=[
                    "Restore from backup if needed",
                    "Restart services if required"
                ],
                escalation_triggers=[
                    "Storage < 200MB",
                    "Services failing to start",
                    "Database connection issues"
                ],
                estimated_time_minutes=20,
                required_permissions=["admin", "system_ops"]
            ),
            
            Runbook(
                id="ev_decline",
                title="EV Performance Decline",
                category=AlertCategory.BUSINESS_METRICS,
                severity=AlertSeverity.HIGH,
                steps=[
                    "1. Analyze EV calculation methodology",
                    "2. Check market data accuracy",
                    "3. Review model probability calibration",
                    "4. Examine line movement patterns",
                    "5. Validate odds provider data"
                ],
                checks=[
                    "SELECT AVG(expected_value) FROM model_picks WHERE created_at > NOW() - INTERVAL '1 hour'",
                    "SELECT AVG(odds) FROM model_picks WHERE created_at > NOW() - INTERVAL '1 hour'",
                    "SELECT COUNT(*) FROM model_picks WHERE expected_value < -0.2"
                ],
                fix_actions=[
                    "Adjust EV calculation thresholds",
                    "Update model probability calibration",
                    "Switch to backup odds provider",
                    "Temporarily reduce recommendation volume"
                ],
                rollback_actions=[
                    "Revert EV calculation changes",
                    "Restore previous calibration",
                    "Switch back to primary data source"
                ],
                escalation_triggers=[
                    "EV < -0.05 for more than 4 hours",
                    "User profitability significantly impacted",
                    "Multiple sports showing EV decline"
                ],
                estimated_time_minutes=60,
                required_permissions=["admin", "model_ops"]
            ),
        ]
    
    def _define_guardrails(self) -> List[Guardrail]:
        """Define safety limits for automated actions."""
        return [
            Guardrail(
                name="data_deletion_limits",
                max_data_deletion_per_cycle_mb=100.0,  # 100MB max per cycle
                max_api_calls_per_hour=1000,
                max_config_changes_per_day=5,
                safe_mode_enabled=True,
                requires_approval_for=["critical_data_deletion", "sport_disable", "model_retraining"],
                explainability_required=True
            ),
            
            Guardrail(
                name="business_metric_changes",
                max_data_deletion_per_cycle_mb=0.0,  # No data deletion
                max_api_calls_per_hour=500,
                max_config_changes_per_day=2,
                safe_mode_enabled=True,
                requires_approval_for=["ev_threshold_change", "hit_rate_threshold_change", "sport_priority_change"],
                explainability_required=True
            ),
            
            Guardrail(
                name="system_health_actions",
                max_data_deletion_per_cycle_mb=500.0,  # Higher limit for system issues
                max_api_calls_per_hour=2000,
                max_config_changes_per_day=10,
                safe_mode_enabled=False,  # Allow more aggressive healing
                requires_approval_for=["database_changes", "service_restart"],
                explainability_required=False
            )
        ]
    
    def _define_metrics(self) -> List[MetricDefinition]:
        """Define SLI-like metrics for production monitoring."""
        return [
            # Service Level Indicators (SLIs)
            MetricDefinition(
                name="data_freshness_latency",
                description="Time from data creation to availability",
                unit="minutes",
                target_value=5.0,
                warning_threshold=10.0,
                critical_threshold=30.0,
                category="freshness",
                sli=True
            ),
            
            MetricDefinition(
                name="recommendation_hit_rate",
                description="Accuracy of betting recommendations",
                unit="percentage",
                target_value=0.55,
                warning_threshold=0.45,
                critical_threshold=0.30,
                category="accuracy",
                sli=True
            ),
            
            MetricDefinition(
                name="system_availability",
                description="Brain service uptime",
                unit="percentage",
                target_value=0.999,
                warning_threshold=0.995,
                critical_threshold=0.990,
                category="availability",
                sli=True
            ),
            
            # Supporting metrics
            MetricDefinition(
                name="bad_prop_rate",
                description="Percentage of props with data quality issues",
                unit="percentage",
                target_value=0.01,
                warning_threshold=0.05,
                critical_threshold=0.10,
                category="data_quality",
                sli=False
            ),
            
            MetricDefinition(
                name="healed_incident_success_rate",
                description="Success rate of automated healing actions",
                unit="percentage",
                target_value=0.90,
                warning_threshold=0.75,
                critical_threshold=0.50,
                category="healing",
                sli=False
            ),
            
            MetricDefinition(
                name="api_response_time_p95",
                description="95th percentile API response time",
                unit="milliseconds",
                target_value=1000.0,
                warning_threshold=2000.0,
                critical_threshold=5000.0,
                category="performance",
                sli=False
            ),
            
            MetricDefinition(
                name="average_ev",
                description="Average expected value of recommendations",
                unit="decimal",
                target_value=0.05,
                warning_threshold=0.01,
                critical_threshold=-0.01,
                category="business",
                sli=False
            ),
        ]
    
    def _define_policies(self) -> Dict[str, Any]:
        """Define operational policies for the brain service."""
        return {
            "quiet_hours": {
                "weekdays": ["01:00-06:00"],  # 1 AM - 6 AM
                "weekends": ["02:00-07:00"],  # 2 AM - 7 AM
            },
            "escalation_policies": {
                "critical": {"escalate_after_minutes": 30, "max_escalations": 3},
                "high": {"escalate_after_minutes": 120, "max_escalations": 2},
                "medium": {"escalate_after_minutes": 240, "max_escalations": 1},
                "low": {"escalate_after_minutes": 480, "max_escalations": 1},
            },
            "approval_policies": {
                "requires_manual_approval": [
                    "critical_data_deletion",
                    "sport_disable",
                    "model_retraining",
                    "ev_threshold_change",
                    "hit_rate_threshold_change"
                ],
                "auto_approval": [
                    "cache_clearing",
                    "log_rotation",
                    "temporary_file_cleanup",
                    "baseline_adjustment"
                ]
            },
            "trace_sampling": {
                "high_value_operations": 1.0,  # 100% sampling
                "normal_operations": 0.1,   # 10% sampling
                "error_operations": 1.0,     # 100% sampling
                "max_traces_per_hour": 1000
            },
            "data_retention": {
                "correlation_traces": 30,      # days
                "decision_logs": 90,          # days
                "anomaly_history": 180,       # days
                "business_metrics": 365,       # days
                "debug_logs": 7               # days
            }
        }
    
    def _define_deployment_checklist(self) -> List[str]:
        """Checklist for deploying new brain features."""
        return [
            "✅ Alert rules defined and tested",
            "✅ Runbooks created and reviewed",
            "✅ Guardrails configured and tested",
            "✅ Metrics taxonomy defined and dashboards created",
            "✅ Correlation ID tracking verified end-to-end",
            "✅ Trace sampling strategy implemented",
            "✅ Cross-linking between logs/metrics/traces working",
            "✅ Safe mode and dry-run functionality tested",
            "✅ Approval workflows configured",
            "✅ On-call team trained on runbooks",
            "✅ Quiet hours and escalation policies set",
            "✅ Data retention policies configured",
            "✅ Production readiness checklist completed",
            "✅ Rollback plan documented and tested"
        ]

# Global production configuration instance
production_config = ProductionConfig()
