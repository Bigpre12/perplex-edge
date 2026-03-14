"""
Global in-memory app state singleton.
FIX #5: app.core.state was completely missing → caused Brain Health 500.
"""
from datetime import datetime, timezone
from typing import Any

class AppState:
    def __init__(self):
        self.started_at = datetime.now(timezone.utc)
        self.healing_actions: list = []
        self.last_health_check: str | None = None
        self.system_metrics: dict[str, Any] = {}
        self.brain_decisions: list = []

    def record_healing_action(self, action: str, component: str):
        self.healing_actions.append({
            "action": action,
            "component": component,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        if len(self.healing_actions) > 100:
            self.healing_actions = self.healing_actions[-100:]

    def update_metrics(self, metrics: dict):
        self.system_metrics.update(metrics)
        self.last_health_check = datetime.now(timezone.utc).isoformat()

    def record_brain_decision(self, decision: dict):
        self.brain_decisions.append({
            **decision,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        if len(self.brain_decisions) > 200:
            self.brain_decisions = self.brain_decisions[-200:]

app_state = AppState()
