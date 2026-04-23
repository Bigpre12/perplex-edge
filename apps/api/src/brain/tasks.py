"""
Celery tasks for the Active Brain.

Scheduled odds ingestion uses ``workers.ev_engine.run_ev_cycle_task``, which calls
``unified_ingestion.run`` — that path already runs ``BrainGovernor.plan_ingest``
before any network fetch. Add optional diagnostic tasks here only if they must
run on a separate beat entry.
"""
from __future__ import annotations

__all__: list[str] = []
