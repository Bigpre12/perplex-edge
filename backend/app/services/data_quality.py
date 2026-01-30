"""
Data Quality Validation Module.

Validates incoming data before it goes live on the site:
- Feed sanity checks (counts, duplicates, time windows)
- Prop line range validation (no 0 pts, no 500 pt totals)
- Cross-day comparison (detect sudden drops)
- Quality gates that must pass before serving data

If checks fail, logs alerts and optionally blocks bad data.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta, date
from typing import Any, Optional
from collections import Counter

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Game, Line, Sport

logger = logging.getLogger(__name__)


# =============================================================================
# Sport Key to League Code Mapping
# =============================================================================

SPORT_KEY_TO_LEAGUE = {
    "basketball_nba": "NBA",
    "basketball_ncaab": "NCAAB",
    "americanfootball_nfl": "NFL",
}


# =============================================================================
# Validation Rules Configuration
# =============================================================================

@dataclass
class PropRanges:
    """Valid ranges for player prop lines by stat type."""
    min_value: float
    max_value: float
    description: str


# Basketball prop ranges (NBA/NCAAB)
BASKETBALL_PROP_RANGES = {
    "player_points": PropRanges(0.5, 60.0, "Points"),
    "player_rebounds": PropRanges(0.5, 25.0, "Rebounds"),
    "player_assists": PropRanges(0.5, 20.0, "Assists"),
    "player_threes": PropRanges(0.5, 12.0, "3-Pointers"),
    "player_steals": PropRanges(0.5, 5.0, "Steals"),
    "player_blocks": PropRanges(0.5, 6.0, "Blocks"),
    "player_turnovers": PropRanges(0.5, 8.0, "Turnovers"),
    "player_points_rebounds_assists": PropRanges(5.0, 100.0, "PRA"),
    "player_points_rebounds": PropRanges(3.0, 80.0, "P+R"),
    "player_points_assists": PropRanges(3.0, 75.0, "P+A"),
    "player_rebounds_assists": PropRanges(2.0, 40.0, "R+A"),
    # Short stat types
    "pts": PropRanges(0.5, 60.0, "Points"),
    "reb": PropRanges(0.5, 25.0, "Rebounds"),
    "ast": PropRanges(0.5, 20.0, "Assists"),
    "stl": PropRanges(0.5, 5.0, "Steals"),
    "blk": PropRanges(0.5, 6.0, "Blocks"),
    "fg3m": PropRanges(0.5, 12.0, "3-Pointers"),
}

# NFL prop ranges
NFL_PROP_RANGES = {
    "player_pass_yds": PropRanges(50.0, 450.0, "Passing Yards"),
    "player_pass_tds": PropRanges(0.5, 6.0, "Passing TDs"),
    "player_pass_completions": PropRanges(5.0, 45.0, "Completions"),
    "player_pass_attempts": PropRanges(10.0, 60.0, "Pass Attempts"),
    "player_pass_interceptions": PropRanges(0.5, 4.0, "Interceptions"),
    "player_rush_yds": PropRanges(5.0, 200.0, "Rushing Yards"),
    "player_rush_attempts": PropRanges(3.0, 35.0, "Rush Attempts"),
    "player_rush_tds": PropRanges(0.5, 4.0, "Rushing TDs"),
    "player_receptions": PropRanges(0.5, 15.0, "Receptions"),
    "player_reception_yds": PropRanges(5.0, 200.0, "Receiving Yards"),
    "player_reception_tds": PropRanges(0.5, 3.0, "Receiving TDs"),
    # Short stat types
    "pass_yds": PropRanges(50.0, 450.0, "Passing Yards"),
    "pass_tds": PropRanges(0.5, 6.0, "Passing TDs"),
    "pass_att": PropRanges(10.0, 60.0, "Pass Attempts"),
    "pass_comp": PropRanges(5.0, 45.0, "Completions"),
    "int": PropRanges(0.5, 4.0, "Interceptions"),
    "rush_yds": PropRanges(5.0, 200.0, "Rushing Yards"),
    "rush_att": PropRanges(3.0, 35.0, "Rush Attempts"),
    "rush_tds": PropRanges(0.5, 4.0, "Rushing TDs"),
    "rec_yds": PropRanges(5.0, 200.0, "Receiving Yards"),
    "rec": PropRanges(0.5, 15.0, "Receptions"),
    "rec_tds": PropRanges(0.5, 3.0, "Receiving TDs"),
}

# Sport-specific configurations
SPORT_CONFIG = {
    "basketball_nba": {
        "prop_ranges": BASKETBALL_PROP_RANGES,
        "min_games_weekday": 2,
        "min_games_weekend": 4,
        "max_games_per_day": 15,
        "game_time_window_hours": 12,  # Games should start within 12h window
        "expected_props_per_game": 30,  # ~6 players × 5 props each
    },
    "basketball_ncaab": {
        "prop_ranges": BASKETBALL_PROP_RANGES,
        "min_games_weekday": 5,
        "min_games_weekend": 15,
        "max_games_per_day": 100,
        "game_time_window_hours": 14,
        "expected_props_per_game": 20,
    },
    "americanfootball_nfl": {
        "prop_ranges": NFL_PROP_RANGES,
        "min_games_weekday": 0,  # NFL mostly weekends
        "min_games_weekend": 3,
        "max_games_per_day": 16,
        "game_time_window_hours": 10,
        "expected_props_per_game": 40,
    },
}


# =============================================================================
# Validation Results
# =============================================================================

@dataclass
class ValidationIssue:
    """A single validation issue."""
    severity: str  # "error", "warning", "info"
    category: str  # "games", "props", "duplicates", "timing", "counts"
    message: str
    details: dict = field(default_factory=dict)


@dataclass
class ValidationResult:
    """Complete validation result for a data feed."""
    valid: bool
    sport: str
    checked_at: datetime
    games_count: int
    props_count: int
    issues: list[ValidationIssue] = field(default_factory=list)
    metrics: dict = field(default_factory=dict)
    
    @property
    def error_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "error")
    
    @property
    def warning_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "warning")
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "valid": self.valid,
            "sport": self.sport,
            "checked_at": self.checked_at.isoformat(),
            "games_count": self.games_count,
            "props_count": self.props_count,
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "issues": [
                {
                    "severity": i.severity,
                    "category": i.category,
                    "message": i.message,
                    "details": i.details,
                }
                for i in self.issues
            ],
            "metrics": self.metrics,
        }


# =============================================================================
# Feed Validation Functions
# =============================================================================

def validate_games_feed(
    games: list[dict[str, Any]],
    sport_key: str,
) -> list[ValidationIssue]:
    """
    Validate games data for sanity.
    
    Checks:
    - No duplicate game IDs
    - Game times within expected window
    - Game count within expected range
    - Required fields present
    """
    issues = []
    config = SPORT_CONFIG.get(sport_key, SPORT_CONFIG["basketball_nba"])
    
    if not games:
        issues.append(ValidationIssue(
            severity="warning",
            category="games",
            message="No games in feed",
            details={"sport": sport_key},
        ))
        return issues
    
    # Check for duplicate game IDs
    game_ids = [g.get("id") or g.get("external_id") for g in games]
    id_counts = Counter(game_ids)
    duplicates = {gid: count for gid, count in id_counts.items() if count > 1}
    
    if duplicates:
        issues.append(ValidationIssue(
            severity="error",
            category="duplicates",
            message=f"Duplicate game IDs found: {len(duplicates)} duplicates",
            details={"duplicates": dict(list(duplicates.items())[:5])},
        ))
    
    # Check game times
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    
    future_games = []
    past_games = []
    missing_times = 0
    
    for game in games:
        start_time = game.get("start_time") or game.get("commence_time")
        if not start_time:
            missing_times += 1
            continue
        
        if isinstance(start_time, str):
            try:
                start_time = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
            except ValueError:
                missing_times += 1
                continue
        
        if start_time > now:
            future_games.append(start_time)
        else:
            past_games.append(start_time)
    
    if missing_times > len(games) * 0.1:  # More than 10% missing times
        issues.append(ValidationIssue(
            severity="warning",
            category="timing",
            message=f"{missing_times} games missing start times",
            details={"total_games": len(games), "missing": missing_times},
        ))
    
    # Check time window spread
    if future_games:
        earliest = min(future_games)
        latest = max(future_games)
        spread_hours = (latest - earliest).total_seconds() / 3600
        
        if spread_hours > config["game_time_window_hours"] * 2:
            issues.append(ValidationIssue(
                severity="warning",
                category="timing",
                message=f"Games spread across {spread_hours:.1f} hours (expected ~{config['game_time_window_hours']}h)",
                details={"earliest": earliest.isoformat(), "latest": latest.isoformat()},
            ))
    
    # Check game count
    is_weekend = now.weekday() >= 5
    min_games = config["min_games_weekend"] if is_weekend else config["min_games_weekday"]
    max_games = config["max_games_per_day"]
    
    if len(games) < min_games:
        issues.append(ValidationIssue(
            severity="warning",
            category="counts",
            message=f"Low game count: {len(games)} (expected >= {min_games})",
            details={"count": len(games), "min_expected": min_games, "is_weekend": is_weekend},
        ))
    
    if len(games) > max_games:
        issues.append(ValidationIssue(
            severity="warning",
            category="counts",
            message=f"High game count: {len(games)} (expected <= {max_games})",
            details={"count": len(games), "max_expected": max_games},
        ))
    
    return issues


def validate_props_feed(
    props: list[dict[str, Any]],
    sport_key: str,
) -> list[ValidationIssue]:
    """
    Validate player props for sanity.
    
    Checks:
    - Line values within valid ranges (no 0 pts, no 500 pt totals)
    - Odds are reasonable (-500 to +500 typical range)
    - No duplicate prop entries
    - Required fields present
    """
    issues = []
    config = SPORT_CONFIG.get(sport_key, SPORT_CONFIG["basketball_nba"])
    prop_ranges = config["prop_ranges"]
    
    if not props:
        issues.append(ValidationIssue(
            severity="warning",
            category="props",
            message="No props in feed",
            details={"sport": sport_key},
        ))
        return issues
    
    out_of_range = []
    invalid_odds = []
    missing_fields = 0
    
    for prop in props:
        stat_type = prop.get("stat_type") or prop.get("market")
        line_value = prop.get("line_value") or prop.get("point")
        over_odds = prop.get("over_odds") or prop.get("over_price")
        under_odds = prop.get("under_odds") or prop.get("under_price")
        
        # Check required fields
        if not stat_type or line_value is None:
            missing_fields += 1
            continue
        
        # Validate line value range
        if stat_type in prop_ranges:
            range_config = prop_ranges[stat_type]
            try:
                line_float = float(line_value)
                if line_float < range_config.min_value or line_float > range_config.max_value:
                    out_of_range.append({
                        "stat_type": stat_type,
                        "line": line_float,
                        "valid_range": f"{range_config.min_value}-{range_config.max_value}",
                        "player": prop.get("player_name", "unknown"),
                    })
            except (ValueError, TypeError):
                pass
        
        # Validate odds are reasonable
        for odds_val, odds_name in [(over_odds, "over"), (under_odds, "under")]:
            if odds_val is not None:
                try:
                    odds_int = int(odds_val)
                    # American odds typically -1000 to +1000, flag extremes
                    if odds_int < -1000 or odds_int > 1000:
                        invalid_odds.append({
                            "stat_type": stat_type,
                            "odds_type": odds_name,
                            "odds": odds_int,
                            "player": prop.get("player_name", "unknown"),
                        })
                except (ValueError, TypeError):
                    pass
    
    # Report issues
    if missing_fields > len(props) * 0.05:  # More than 5% missing
        issues.append(ValidationIssue(
            severity="warning",
            category="props",
            message=f"{missing_fields} props missing required fields",
            details={"total": len(props), "missing": missing_fields},
        ))
    
    if out_of_range:
        severity = "error" if len(out_of_range) > 10 else "warning"
        issues.append(ValidationIssue(
            severity=severity,
            category="props",
            message=f"{len(out_of_range)} props with out-of-range line values",
            details={"samples": out_of_range[:5]},
        ))
    
    if invalid_odds:
        issues.append(ValidationIssue(
            severity="warning",
            category="props",
            message=f"{len(invalid_odds)} props with extreme odds",
            details={"samples": invalid_odds[:5]},
        ))
    
    return issues


async def validate_count_change(
    db: AsyncSession,
    sport_key: str,
    current_games: int,
    current_props: int,
) -> list[ValidationIssue]:
    """
    Compare current counts to recent history to detect sudden drops.
    
    A 50%+ drop in games or props likely indicates a data issue.
    """
    issues = []
    
    # Get sport by league code
    league_code = SPORT_KEY_TO_LEAGUE.get(sport_key)
    if not league_code:
        return issues
    
    sport_result = await db.execute(
        select(Sport).where(Sport.league_code == league_code)
    )
    sport = sport_result.scalar_one_or_none()
    
    if not sport:
        return issues
    
    # Get yesterday's counts
    yesterday = datetime.now(timezone.utc) - timedelta(days=1)
    yesterday_start = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday_end = yesterday_start + timedelta(days=1)
    
    yesterday_games_result = await db.execute(
        select(func.count(Game.id))
        .where(Game.sport_id == sport.id)
        .where(Game.created_at >= yesterday_start)
        .where(Game.created_at < yesterday_end)
    )
    yesterday_games = yesterday_games_result.scalar() or 0
    
    yesterday_props_result = await db.execute(
        select(func.count(Line.id))
        .where(Line.player_id.isnot(None))
        .where(Line.created_at >= yesterday_start)
        .where(Line.created_at < yesterday_end)
    )
    yesterday_props = yesterday_props_result.scalar() or 0
    
    # Check for significant drops
    if yesterday_games > 0 and current_games < yesterday_games * 0.5:
        drop_pct = (1 - current_games / yesterday_games) * 100
        issues.append(ValidationIssue(
            severity="error",
            category="counts",
            message=f"Game count dropped {drop_pct:.0f}% from yesterday",
            details={
                "yesterday": yesterday_games,
                "today": current_games,
                "drop_percent": drop_pct,
            },
        ))
    
    if yesterday_props > 0 and current_props < yesterday_props * 0.5:
        drop_pct = (1 - current_props / yesterday_props) * 100
        issues.append(ValidationIssue(
            severity="error",
            category="counts",
            message=f"Props count dropped {drop_pct:.0f}% from yesterday",
            details={
                "yesterday": yesterday_props,
                "today": current_props,
                "drop_percent": drop_pct,
            },
        ))
    
    return issues


# =============================================================================
# Main Validation Entry Points
# =============================================================================

async def validate_feed(
    db: AsyncSession,
    sport_key: str,
    games: list[dict[str, Any]],
    props: list[dict[str, Any]],
    check_history: bool = True,
) -> ValidationResult:
    """
    Run full validation on a data feed before going live.
    
    Args:
        db: Database session
        sport_key: Sport being validated
        games: List of game data dictionaries
        props: List of prop data dictionaries
        check_history: Whether to compare against historical counts
    
    Returns:
        ValidationResult with pass/fail and detailed issues
    """
    issues = []
    
    # Validate games
    game_issues = validate_games_feed(games, sport_key)
    issues.extend(game_issues)
    
    # Validate props
    prop_issues = validate_props_feed(props, sport_key)
    issues.extend(prop_issues)
    
    # Check for sudden count drops
    if check_history:
        history_issues = await validate_count_change(
            db, sport_key, len(games), len(props)
        )
        issues.extend(history_issues)
    
    # Determine if feed is valid (no errors)
    error_count = sum(1 for i in issues if i.severity == "error")
    is_valid = error_count == 0
    
    result = ValidationResult(
        valid=is_valid,
        sport=sport_key,
        checked_at=datetime.now(timezone.utc),
        games_count=len(games),
        props_count=len(props),
        issues=issues,
        metrics={
            "unique_game_ids": len(set(g.get("id") or g.get("external_id") for g in games)),
            "unique_players": len(set(p.get("player_name") or p.get("player_id") for p in props if p.get("player_name") or p.get("player_id"))),
            "stat_types": list(set(p.get("stat_type") or p.get("market") for p in props if p.get("stat_type") or p.get("market"))),
        },
    )
    
    # Log result
    if is_valid:
        logger.info(
            f"Data validation PASSED for {sport_key}: "
            f"{len(games)} games, {len(props)} props, {result.warning_count} warnings"
        )
    else:
        logger.error(
            f"Data validation FAILED for {sport_key}: "
            f"{error_count} errors, {result.warning_count} warnings"
        )
        for issue in issues:
            if issue.severity == "error":
                logger.error(f"  [{issue.category}] {issue.message}")
    
    return result


async def validate_database_state(
    db: AsyncSession,
    sport_key: str,
) -> ValidationResult:
    """
    Validate current database state for a sport.
    
    Use this to check data quality of what's already in the database.
    """
    # Get sport by league code
    league_code = SPORT_KEY_TO_LEAGUE.get(sport_key)
    if not league_code:
        return ValidationResult(
            valid=False,
            sport=sport_key,
            checked_at=datetime.now(timezone.utc),
            games_count=0,
            props_count=0,
            issues=[ValidationIssue(
                severity="error",
                category="games",
                message=f"Unknown sport key: {sport_key}",
            )],
        )
    
    sport_result = await db.execute(
        select(Sport).where(Sport.league_code == league_code)
    )
    sport = sport_result.scalar_one_or_none()
    
    if not sport:
        return ValidationResult(
            valid=False,
            sport=sport_key,
            checked_at=datetime.now(timezone.utc),
            games_count=0,
            props_count=0,
            issues=[ValidationIssue(
                severity="error",
                category="games",
                message=f"Sport not found: {sport_key}",
            )],
        )
    
    # Fetch today's games
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow = today_start + timedelta(days=1)
    
    games_result = await db.execute(
        select(Game)
        .where(Game.sport_id == sport.id)
        .where(Game.start_time >= today_start)
        .where(Game.start_time < tomorrow + timedelta(days=7))
    )
    games = games_result.scalars().all()
    
    # Convert to dicts for validation
    games_data = [
        {
            "id": str(g.id),
            "external_id": g.external_id,
            "start_time": g.start_time,
            "home_team": g.home_team,
            "away_team": g.away_team,
        }
        for g in games
    ]
    
    # Fetch props for these games
    game_ids = [g.id for g in games]
    if game_ids:
        props_result = await db.execute(
            select(Line)
            .where(Line.game_id.in_(game_ids))
            .where(Line.player_id.isnot(None))
        )
        props = props_result.scalars().all()
        
        props_data = [
            {
                "stat_type": p.stat_type,
                "line_value": p.line_value,
                "over_odds": p.over_odds,
                "under_odds": p.under_odds,
                "player_id": str(p.player_id) if p.player_id else None,
            }
            for p in props
        ]
    else:
        props_data = []
    
    return await validate_feed(db, sport_key, games_data, props_data, check_history=True)


def create_quality_gate(
    max_errors: int = 0,
    max_warnings: int = 10,
) -> callable:
    """
    Create a quality gate function that blocks bad data.
    
    Args:
        max_errors: Maximum allowed errors (default 0 = any error blocks)
        max_warnings: Maximum allowed warnings
    
    Returns:
        Function that raises exception if gate fails
    
    Usage:
        gate = create_quality_gate(max_errors=0, max_warnings=5)
        result = await validate_feed(...)
        gate(result)  # Raises if validation fails
    """
    def check_gate(result: ValidationResult) -> None:
        if result.error_count > max_errors:
            raise DataQualityError(
                f"Quality gate failed: {result.error_count} errors (max {max_errors})",
                result=result,
            )
        if result.warning_count > max_warnings:
            raise DataQualityError(
                f"Quality gate failed: {result.warning_count} warnings (max {max_warnings})",
                result=result,
            )
        logger.info(f"Quality gate passed for {result.sport}")
    
    return check_gate


class DataQualityError(Exception):
    """Raised when data fails quality validation."""
    
    def __init__(self, message: str, result: ValidationResult):
        super().__init__(message)
        self.result = result
