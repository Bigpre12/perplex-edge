"""
Data Services - Orchestration Layer.

Services combine:
- Multiple providers (with fallback order)
- Caching (live vs historical)
- Data normalization
- Response envelopes (source, last_updated, season)

Services do NOT:
- Talk to external APIs directly (use providers)
- Write to the database (use repositories)
"""

from app.data.services.odds import OddsService
from app.data.services.schedules import ScheduleService
from app.data.services.stats import StatsService
from app.data.services.injuries import InjuryService

__all__ = [
    "OddsService",
    "ScheduleService",
    "StatsService",
    "InjuryService",
]
