"""Active Brain governor: quota-aware ingest decisions before TheOddsAPI traffic."""

from brain.engine import brain_governor, IngestPlan

__all__ = ["brain_governor", "IngestPlan"]
