"""Service providers and ETL functions for external data sources."""

# Providers
from app.services.odds_provider import OddsProvider, XYZOddsProvider, get_quota_status
from app.services.stats_provider import StatsProvider
from app.services.injury_provider import InjuryProvider
from app.services.roster_provider import RosterProvider

# ETL Functions
from app.services.etl_games_and_lines import (
    sync_games_and_lines,
    sync_all_sports,
    sync_with_fallback,
)
from app.services.etl_stats import (
    sync_recent_player_stats,
    sync_player_stats_by_days,
    sync_single_player_stats,
)
from app.services.etl_injuries import (
    sync_injuries,
    sync_all_injuries,
    clear_old_injuries,
)
from app.services.etl_rosters import (
    sync_rosters,
    update_player_team,
    sync_player_team_from_roster_api,
)

# Picks Generator
from app.services.picks_generator import (
    generate_picks,
    generate_all_picks,
)

# Results Tracker
from app.services.results_tracker import ResultsTracker

# Snapshot Service
from app.services.snapshot_service import (
    save_daily_snapshot,
    load_snapshot,
    list_snapshots,
    delete_old_snapshots,
    check_sync_health,
    run_all_health_checks,
    pre_refresh_snapshot,
    post_sync_validation,
)

# Data Quality
from app.services.data_quality import (
    validate_feed,
    validate_database_state,
    create_quality_gate,
    DataQualityError,
)

# API Monitoring
from app.services.api_monitor import (
    get_api_monitor,
    log_api_call,
    track_api_call,
)

# Calibration Service
from app.services.calibration_service import (
    calculate_clv,
    calculate_profit_loss,
    calculate_brier_score,
    compute_calibration_metrics,
    store_calibration_metrics,
    get_reliability_data,
    get_roi_by_confidence,
    get_clv_analysis,
)

# Model Functions
from app.services.model import (
    american_to_implied_prob,
    implied_prob_to_decimal,
    compute_ev,
    compute_player_prop_model_probabilities,
    generate_model_picks_for_today,
    generate_all_model_picks,
)

__all__ = [
    # Providers
    "OddsProvider",
    "XYZOddsProvider",
    "StatsProvider",
    "InjuryProvider",
    "RosterProvider",
    # Quota Tracking
    "get_quota_status",
    # ETL - Games & Lines
    "sync_games_and_lines",
    "sync_all_sports",
    "sync_with_fallback",
    # ETL - Stats
    "sync_recent_player_stats",
    "sync_player_stats_by_days",
    "sync_single_player_stats",
    # ETL - Injuries
    "sync_injuries",
    "sync_all_injuries",
    "clear_old_injuries",
    # ETL - Rosters
    "sync_rosters",
    "update_player_team",
    "sync_player_team_from_roster_api",
    # Picks Generator
    "generate_picks",
    "generate_all_picks",
    # Results Tracker
    "ResultsTracker",
    # Model Functions
    "american_to_implied_prob",
    "implied_prob_to_decimal",
    "compute_ev",
    "compute_player_prop_model_probabilities",
    "generate_model_picks_for_today",
    "generate_all_model_picks",
    # Snapshot Service
    "save_daily_snapshot",
    "load_snapshot",
    "list_snapshots",
    "delete_old_snapshots",
    "check_sync_health",
    "run_all_health_checks",
    "pre_refresh_snapshot",
    "post_sync_validation",
    # Data Quality
    "validate_feed",
    "validate_database_state",
    "create_quality_gate",
    "DataQualityError",
    # API Monitoring
    "get_api_monitor",
    "log_api_call",
    "track_api_call",
    # Calibration Service
    "calculate_clv",
    "calculate_profit_loss",
    "calculate_brier_score",
    "compute_calibration_metrics",
    "store_calibration_metrics",
    "get_reliability_data",
    "get_roi_by_confidence",
    "get_clv_analysis",
]
