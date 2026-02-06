"""
Dry-run and evaluation framework for brain service.
Allows testing healing actions without actually executing them.
"""

import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)

class DryRunMode(Enum):
    PROPOSED = "proposed"      # Log what would happen, don't execute
    SHADOW = "shadow"          # Execute alongside production for comparison
    SIMULATION = "simulation"    # Re-run historical scenarios

@dataclass
class DryRunAction:
    """Represents a proposed action in dry-run mode."""
    action_type: str
    component: str
    reasoning: str
    estimated_impact: Dict[str, Any]
    would_execute: bool = True
    requires_approval: bool = False
    safe_mode_bypass: bool = False

@dataclass
class DryRunResult:
    """Result of a dry-run evaluation."""
    cycle_id: str
    timestamp: datetime
    proposed_actions: List[DryRunAction]
    executed_actions: List[DryRunAction]
    prevented_actions: List[DryRunAction]
    impact_assessment: Dict[str, Any]
    recommendations: List[str]

class DryRunManager:
    """Manages dry-run mode for brain service operations."""
    
    def __init__(self, mode: DryRunMode = DryRunMode.PROPOSED):
        self.mode = mode
        self.action_history: List[DryRunResult] = []
        self.current_cycle_actions: List[DryRunAction] = []
        self.safe_mode = True
        self.approval_required_actions = [
            "critical_data_deletion",
            "sport_disable",
            "model_retraining",
            "ev_threshold_change"
        ]
    
    def start_cycle(self) -> str:
        """Start a new dry-run cycle."""
        cycle_id = f"dryrun_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
        self.current_cycle_actions = []
        logger.info(f"[DRYRUN] Starting {self.mode.value} cycle: {cycle_id}")
        return cycle_id
    
    def propose_action(self, action_type: str, component: str, reasoning: str, 
                       estimated_impact: Dict[str, Any], requires_approval: bool = False) -> bool:
        """Propose an action for evaluation."""
        
        action = DryRunAction(
            action_type=action_type,
            component=component,
            reasoning=reasoning,
            estimated_impact=estimated_impact,
            would_execute=self._should_execute(action_type, requires_approval),
            requires_approval=requires_approval,
            safe_mode_bypass=False
        )
        
        self.current_cycle_actions.append(action)
        
        # Log the proposed action
        logger.info(f"[DRYRUN] Proposed: {action_type} on {component} - {reasoning}")
        
        return action.would_execute
    
    def _should_execute(self, action_type: str, requires_approval: bool) -> bool:
        """Determine if action should execute based on mode and policies."""
        if self.mode == DryRunMode.PROPOSED:
            return False  # Never execute in proposed mode
        
        if self.safe_mode and action_type in self.approval_required_actions:
            return False  # Requires manual approval in safe mode
        
        if requires_approval and self.mode != DryRunMode.SIMULATION:
            return False  # Requires manual approval
        
        return True
    
    def evaluate_impact(self, executed_actions: List[DryRunAction]) -> Dict[str, Any]:
        """Evaluate the impact of executed actions."""
        impact = {
            "data_volume_affected": 0,
            "users_impacted": 0,
            "revenue_impact": 0.0,
            "performance_impact": 0.0,
            "risk_level": "low"
        }
        
        for action in executed_actions:
            # Estimate impact based on action type
            if "data_deletion" in action.action_type:
                impact["data_volume_affected"] += action.estimated_impact.get("records_affected", 0)
                impact["risk_level"] = "high"
            
            elif "cache_clear" in action.action_type:
                impact["performance_impact"] += action.estimated_impact.get("performance_gain", 0)
                impact["risk_level"] = "low"
            
            elif "baseline_adjust" in action.action_type:
                impact["risk_level"] = "medium"
        
        return impact
    
    def complete_cycle(self, cycle_id: str, executed_actions: List[DryRunAction]) -> DryRunResult:
        """Complete a dry-run cycle and generate results."""
        
        # Prevented actions are those that would have executed but were blocked
        prevented_actions = [
            action for action in self.current_cycle_actions 
            if action.requires_approval and not action.would_execute
        ]
        
        # Evaluate impact of executed actions
        impact_assessment = self.evaluate_impact(executed_actions)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            self.current_cycle_actions, executed_actions, prevented_actions
        )
        
        result = DryRunResult(
            cycle_id=cycle_id,
            timestamp=datetime.now(timezone.utc),
            proposed_actions=self.current_cycle_actions.copy(),
            executed_actions=executed_actions.copy(),
            prevented_actions=prevented_actions,
            impact_assessment=impact_assessment,
            recommendations=recommendations
        )
        
        self.action_history.append(result)
        
        # Keep only last 100 cycles
        if len(self.action_history) > 100:
            self.action_history = self.action_history[-100:]
        
        logger.info(f"[DRYRUN] Completed cycle {cycle_id}: "
                   f"{len(executed_actions)} executed, {len(prevented_actions)} prevented")
        
        return result
    
    def _generate_recommendations(self, proposed: List[DryRunAction], 
                              executed: List[DryRunAction], 
                              prevented: List[DryRunAction]) -> List[str]:
        """Generate recommendations based on dry-run results."""
        recommendations = []
        
        if len(prevented_actions) > 0:
            recommendations.append(
                f"Consider enabling auto-approval for {len(prevented_actions)} safe actions"
            )
        
        if len(executed_actions) == 0:
            recommendations.append("No actions executed - system appears healthy")
        
        high_impact_actions = [a for a in executed_actions if a.estimated_impact.get("risk_level") == "high"]
        if high_impact_actions:
            recommendations.append(
                f"Monitor {len(high_impact_actions)} high-impact actions closely"
            )
        
        return recommendations

class EvaluationFramework:
    """Framework for evaluating brain service effectiveness."""
    
    def __init__(self):
        self.metrics_history = []
        self.experiments = []
        self.current_experiment = None
    
    def start_experiment(self, name: str, description: str, duration_days: int = 7) -> str:
        """Start a new evaluation experiment."""
        experiment_id = f"exp_{name}_{datetime.now(timezone.utc).strftime('%Y%m%d')}"
        
        self.current_experiment = {
            "id": experiment_id,
            "name": name,
            "description": description,
            "start_date": datetime.now(timezone.utc),
            "end_date": datetime.now(timezone.utc) + timedelta(days=duration_days),
            "baseline_metrics": self._capture_baseline_metrics(),
            "current_metrics": {},
            "status": "running"
        }
        
        self.experiments.append(self.current_experiment)
        logger.info(f"[EVAL] Started experiment: {name} ({experiment_id})")
        
        return experiment_id
    
    def _capture_baseline_metrics(self) -> Dict[str, float]:
        """Capture baseline metrics for comparison."""
        # This would capture current system metrics
        return {
            "hit_rate": 0.55,  # Would get from business metrics
            "average_ev": 0.05,
            "prop_volume": 1000,
            "heal_success_rate": 0.90,
            "data_quality_score": 0.95
        }
    
    def update_experiment_metrics(self, experiment_id: str, metrics: Dict[str, float]):
        """Update metrics for an ongoing experiment."""
        for exp in self.experiments:
            if exp["id"] == experiment_id:
                exp["current_metrics"] = metrics
                exp["last_updated"] = datetime.now(timezone.utc)
                
                # Check if experiment should end
                if datetime.now(timezone.utc) >= exp["end_date"]:
                    exp["status"] = "completed"
                    self._analyze_experiment_results(exp)
                break
    
    def _analyze_experiment_results(self, experiment: Dict[str, Any]):
        """Analyze results of a completed experiment."""
        baseline = experiment["baseline_metrics"]
        current = experiment["current_metrics"]
        
        results = {}
        for metric, baseline_value in baseline.items():
            if metric in current:
                current_value = current[metric]
                change_pct = ((current_value - baseline_value) / baseline_value * 100) if baseline_value != 0 else 0
                improvement = change_pct > 0
                
                results[metric] = {
                    "baseline": baseline_value,
                    "current": current_value,
                    "change_pct": round(change_pct, 2),
                    "improvement": improvement,
                    "significance": "high" if abs(change_pct) > 10 else "medium" if abs(change_pct) > 5 else "low"
                }
        
        experiment["results"] = results
        experiment["analysis"] = self._generate_analysis(results)
        
        logger.info(f"[EVAL] Experiment {experiment['name']} completed: {experiment['analysis']}")
    
    def _generate_analysis(self, results: Dict[str, Any]) -> str:
        """Generate analysis summary for experiment results."""
        improvements = sum(1 for r in results.values() if r.get("improvement", False))
        total_metrics = len(results)
        
        if improvements == total_metrics:
            return "All metrics improved significantly"
        elif improvements >= total_metrics * 0.7:
            return "Most metrics improved"
        elif improvements >= total_metrics * 0.3:
            return "Some metrics improved"
        else:
            return "Metrics declined or unchanged"
    
    def get_experiment_summary(self, experiment_id: str) -> Optional[Dict[str, Any]]:
        """Get summary of a specific experiment."""
        for exp in self.experiments:
            if exp["id"] == experiment_id:
                return exp
        return None
    
    def compare_before_after(self, before_experiment_id: str, 
                            after_experiment_id: str) -> Dict[str, Any]:
        """Compare metrics before and after an experiment."""
        before = self.get_experiment_summary(before_experiment_id)
        after = self.get_experiment_summary(after_experiment_id)
        
        if not before or not after:
            return {"error": "One or both experiments not found"}
        
        comparison = {
            "before_experiment": before["name"],
            "after_experiment": after["name"],
            "duration_days": (after["end_date"] - before["start_date"]).days,
            "metric_changes": {}
        }
        
        before_metrics = before.get("results", {})
        after_metrics = after.get("results", {})
        
        for metric in before_metrics:
            if metric in after_metrics:
                before_val = before_metrics[metric]
                after_val = after_metrics[metric]
                
                change = after_val["change_pct"]
                improvement = after_val["improvement"]
                
                comparison["metric_changes"][metric] = {
                    "before": before_val["current"],
                    "after": after_val["current"],
                    "change_pct": change,
                    "improvement": improvement,
                    "significance": after_val["significance"]
                }
        
        return comparison

# Global instances
dry_run_manager = DryRunManager()
evaluation_framework = EvaluationFramework()
