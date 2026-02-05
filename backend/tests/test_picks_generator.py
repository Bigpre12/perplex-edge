"""Tests for picks generator: pure utility functions (odds, EV, confidence, 100% window)."""

from app.services.picks_generator import (
    american_odds_to_probability,
    calculate_expected_value,
    calculate_confidence_score,
    check_100_percent_window,
)


# =============================================================================
# Odds Conversion
# =============================================================================

def test_american_odds_negative():
    prob = american_odds_to_probability(-110)
    assert 0.52 < prob < 0.53  # ~52.38%


def test_american_odds_positive():
    prob = american_odds_to_probability(200)
    assert 0.33 < prob < 0.34  # ~33.33%


def test_american_odds_even():
    prob = american_odds_to_probability(100)
    assert prob == 0.5


def test_american_odds_heavy_favorite():
    prob = american_odds_to_probability(-300)
    assert prob == 0.75


# =============================================================================
# Expected Value
# =============================================================================

def test_ev_positive_edge():
    ev = calculate_expected_value(model_prob=0.60, odds=-110)
    assert ev > 0  # model says 60%, market implies ~52% → positive EV


def test_ev_negative_edge():
    ev = calculate_expected_value(model_prob=0.40, odds=-200)
    assert ev < 0  # model says 40%, market implies ~67% → negative EV


def test_ev_breakeven():
    ev = calculate_expected_value(model_prob=0.50, odds=100)
    # At even odds with 50% model prob, EV should be ~0
    assert abs(ev) < 0.01


# =============================================================================
# Confidence Score
# =============================================================================

def test_confidence_high_edge():
    score = calculate_confidence_score(
        model_prob=0.70,
        implied_prob=0.50,
        ev=0.10,
    )
    assert 0.0 <= score <= 1.0
    assert score > 0.5  # big edge → high confidence


def test_confidence_no_edge():
    score = calculate_confidence_score(
        model_prob=0.50,
        implied_prob=0.50,
        ev=0.0,
    )
    assert 0.0 <= score <= 1.0
    assert score < 0.5  # no edge → low confidence


def test_confidence_clamped():
    score = calculate_confidence_score(
        model_prob=0.99,
        implied_prob=0.10,
        ev=0.50,
    )
    assert score <= 1.0


# =============================================================================
# 100% Window Check
# =============================================================================

def test_100_percent_over_all_hit():
    values = [30.0, 28.0, 35.0, 29.0, 31.0]
    result = check_100_percent_window(values, line_value=25.0, side="over")
    assert result["is_100_percent"] is True
    assert result["hit_rate"] == 1.0


def test_100_percent_over_partial():
    values = [20.0, 28.0, 35.0, 29.0, 31.0]
    result = check_100_percent_window(values, line_value=25.0, side="over")
    assert result["is_100_percent"] is False
    assert result["hit_rate"] < 1.0


def test_100_percent_under_all_hit():
    values = [10.0, 12.0, 8.0, 11.0, 9.0]
    result = check_100_percent_window(values, line_value=15.0, side="under")
    assert result["is_100_percent"] is True


def test_100_percent_empty_values():
    result = check_100_percent_window([], line_value=25.0, side="over")
    assert result["is_100_percent"] is False
    assert result["games_count"] == 0
