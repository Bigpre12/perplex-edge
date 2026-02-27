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
    discord_webhook_url: str = ""          # user-defined Discord webhook override 


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

def _load_config_from_disk() -> Optional[PerplexEdgeConfig]:
    """
    Loads saved configuration from edge_settings_storage.json if it exists.
    """
    import json
    import os
    config_path = "edge_settings_storage.json"
    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                saved = json.load(f)
            return PerplexEdgeConfig(
                feed=EdgeFeedConfig(
                    active_edge_model=saved.get("active_edge_model", "baseline"),
                    min_edge_percent=saved.get("min_edge_percent", 2.0),
                    max_edge_percent=saved.get("max_edge_percent", 40.0),
                    min_games_sample=saved.get("min_games_sample", 5),
                    min_bets_volume=saved.get("min_bets_volume", 10),
                    max_juice=saved.get("max_juice", -200.0),
                    include_main_lines=saved.get("include_main_lines", True),
                    discord_webhook_url=saved.get("discord_webhook_url", "")
                ),
                player_page=PlayerPageConfig()
            )
        except Exception as e:
            print(f"Warning: Failed to load config from disk: {e}")
    return None


_cached_config: Optional[PerplexEdgeConfig] = None


def get_edge_config() -> PerplexEdgeConfig:
    """
    Main entry point: call this from your edge calc + routes.
    Uses cached config if available; falls back to disk then defaults.
    """
    global _cached_config

    if _cached_config is not None:
        return _cached_config

    disk_config = _load_config_from_disk()
    if disk_config is not None:
        _cached_config = disk_config
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
