# antigravity_edge_config.py

from dataclasses import dataclass
from typing import Optional, Literal


EdgeModelName = Literal["baseline", "sharp_v2"]


@dataclass
class EdgeFeedConfig:
    # Global edge model selection
    active_edge_model: EdgeModelName = "baseline"

    # Feed thresholds
    min_edge_percent: float = 2.0          # show props with edge >= 8% (lowered for testing)
    max_edge_percent: float = 40.0         # cap display to avoid crazy outliers
    min_games_sample: int = 5              # min games in sample
    min_bets_volume: int = 10              # min historical attempts if you track it
    max_juice: float = -200.0              # ignore props worse than -120 by default (lowered for testing)

    # Feed content filters
    include_main_lines: bool = True
    include_alt_lines: bool = True
    include_ladders: bool = True
    include_same_game: bool = True
    include_unders: bool = True
    include_overs: bool = True

    # Display / ranking behavior
    rank_by: Literal["edge_percent", "win_prob", "custom_score"] = "edge_percent"
    limit_per_slate: int = 150
    limit_per_player: int = 4

    # Experimental flags
    flag_use_closing_line: bool = True
    flag_include_injury_adjustment: bool = True
    flag_include_pace_adjustment: bool = True
    flag_include_usage_adjustment: bool = True
    flag_show_high_risk_edges: bool = False  # if False, hide extreme variance stuff


@dataclass
class PlayerPageConfig:
    # Which sections to render by default
    show_recent_form_chart: bool = True
    show_season_chart: bool = True
    show_matchup_stats: bool = True
    show_usage_stats: bool = True
    show_injury_context: bool = True
    show_team_pace: bool = True

    # When to highlight a trend (e.g. green badge / callout)
    highlight_trend_min_games: int = 5
    highlight_trend_min_hit_rate: float = 0.62     # 62%+
    highlight_trend_min_edge_percent: float = 8.0  # 8%+ model edge

    # Notes / insights toggles
    enable_auto_notes: bool = True
    enable_risk_warnings: bool = True
    enable_alt_line_suggestions: bool = True
    enable_sg_parlay_suggestions: bool = True


@dataclass
class PerplexEdgeConfig:
    feed: EdgeFeedConfig
    player_page: PlayerPageConfig


# ---- HARD DEFAULTS (safe, always available) ----

_DEFAULT_CONFIG = PerplexEdgeConfig(
    feed=EdgeFeedConfig(),
    player_page=PlayerPageConfig(),
)


# ---- OPTIONAL: HOOK FOR DB / REDIS OVERRIDES ----

def _load_config_from_db() -> Optional[PerplexEdgeConfig]:
    """
    TODO: Replace this stub with real DB/Redis load.
    Return None to fall back to hard defaults.
    """
    # Example structure if you later load JSON from DB:
    # row = session.query(EdgeConfigModel).first()
    # if not row:
    #     return None
    # return PerplexEdgeConfig(
    #     feed=EdgeFeedConfig(**row.feed_json),
    #     player_page=PlayerPageConfig(**row.player_page_json),
    # )
    return None


_cached_config: Optional[PerplexEdgeConfig] = None


def get_edge_config() -> PerplexEdgeConfig:
    """
    Main entry point: call this from your edge calc + routes.
    Uses cached config if available; falls back to defaults if DB not set.
    """
    global _cached_config

    if _cached_config is not None:
        return _cached_config

    db_config = _load_config_from_db()
    if db_config is not None:
        _cached_config = db_config
        return _cached_config

    # Fall back to hardcoded defaults
    _cached_config = _DEFAULT_CONFIG
    return _cached_config


def override_config_for_testing(config: PerplexEdgeConfig) -> None:
    """
    Allow tests or local scripts to override the current config.
    """
    global _cached_config
    _cached_config = config
