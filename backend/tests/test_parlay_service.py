"""Tests for parlay service: correlation detection, grading, platform validation."""

from app.services.parlay_service import (
    calculate_grade,
    grade_to_numeric,
    detect_correlations,
    calculate_correlation_risk_score,
    validate_parlay_for_platform,
    CorrelationType,
)


# =============================================================================
# Grade Tests
# =============================================================================

def test_calculate_grade_a():
    assert calculate_grade(0.05) == "A"
    assert calculate_grade(0.10) == "A"


def test_calculate_grade_b():
    assert calculate_grade(0.03) == "B"
    assert calculate_grade(0.049) == "B"


def test_calculate_grade_c():
    assert calculate_grade(0.01) == "C"
    assert calculate_grade(0.029) == "C"


def test_calculate_grade_d():
    assert calculate_grade(0.00) == "D"
    assert calculate_grade(0.009) == "D"


def test_calculate_grade_f():
    assert calculate_grade(-0.01) == "F"
    assert calculate_grade(-1.0) == "F"


def test_grade_to_numeric():
    assert grade_to_numeric("A") == 4
    assert grade_to_numeric("B") == 3
    assert grade_to_numeric("C") == 2
    assert grade_to_numeric("D") == 1
    assert grade_to_numeric("F") == 0
    assert grade_to_numeric("X") == 0  # unknown


# =============================================================================
# Correlation Detection Tests
# =============================================================================

def test_detect_no_correlations():
    legs = [
        {"game_id": 1, "player_id": 10, "stat_type": "PTS", "side": "over"},
        {"game_id": 2, "player_id": 20, "stat_type": "REB", "side": "over"},
    ]
    warnings = detect_correlations(legs)
    assert len(warnings) == 0


def test_detect_same_game():
    legs = [
        {"game_id": 1, "player_id": 10, "stat_type": "PTS", "side": "over"},
        {"game_id": 1, "player_id": 20, "stat_type": "REB", "side": "over"},
    ]
    warnings = detect_correlations(legs)
    types = [w["type"] for w in warnings]
    assert CorrelationType.SAME_GAME in types


def test_detect_same_player_different_stats():
    legs = [
        {"game_id": 1, "player_id": 10, "stat_type": "PTS", "side": "over", "player_name": "Test"},
        {"game_id": 1, "player_id": 10, "stat_type": "REB", "side": "over", "player_name": "Test"},
    ]
    warnings = detect_correlations(legs)
    types = [w["type"] for w in warnings]
    assert CorrelationType.SAME_PLAYER in types


def test_detect_opposing_sides():
    legs = [
        {"game_id": 1, "player_id": 10, "stat_type": "PTS", "side": "over", "player_name": "Test"},
        {"game_id": 1, "player_id": 10, "stat_type": "PTS", "side": "under", "player_name": "Test"},
    ]
    warnings = detect_correlations(legs)
    types = [w["type"] for w in warnings]
    assert CorrelationType.OPPOSING_SIDES in types


def test_detect_stat_ladder():
    legs = [
        {"game_id": 1, "player_id": 10, "stat_type": "PTS", "side": "over", "line": 24.5, "player_name": "Test"},
        {"game_id": 1, "player_id": 10, "stat_type": "PTS", "side": "over", "line": 29.5, "player_name": "Test"},
    ]
    warnings = detect_correlations(legs)
    types = [w["type"] for w in warnings]
    assert CorrelationType.STAT_LADDER in types


# =============================================================================
# Risk Score Tests
# =============================================================================

def test_risk_score_no_warnings():
    score, label = calculate_correlation_risk_score([])
    assert score == 0.0
    assert label == "LOW"


def test_risk_score_high_warnings():
    warnings = [
        {"severity": "high"},
        {"severity": "high"},
        {"severity": "high"},
    ]
    score, label = calculate_correlation_risk_score(warnings)
    assert score > 0.5
    assert label in ("HIGH", "CRITICAL")


def test_risk_score_capped_at_one():
    warnings = [{"severity": "high"}] * 10
    score, _ = calculate_correlation_risk_score(warnings)
    assert score <= 1.0


# =============================================================================
# Platform Validation Tests
# =============================================================================

def test_prizepicks_one_prop_per_player():
    legs = [
        {"player_id": 10, "player_name": "Test", "game_id": 1},
        {"player_id": 10, "player_name": "Test", "game_id": 1},
    ]
    result = validate_parlay_for_platform(legs, "prizepicks")
    assert result["is_valid"] is False
    assert any(v["type"] == "player_limit_exceeded" for v in result["violations"])


def test_prizepicks_valid():
    legs = [
        {"player_id": 10, "player_name": "A", "game_id": 1},
        {"player_id": 20, "player_name": "B", "game_id": 2},
    ]
    result = validate_parlay_for_platform(legs, "prizepicks")
    assert result["is_valid"] is True


def test_draftkings_game_limit():
    legs = [
        {"player_id": i, "player_name": f"P{i}", "game_id": 1}
        for i in range(5)  # 5 props from same game, max is 4
    ]
    result = validate_parlay_for_platform(legs, "draftkings")
    assert result["is_valid"] is False
    assert any(v["type"] == "game_limit_exceeded" for v in result["violations"])
