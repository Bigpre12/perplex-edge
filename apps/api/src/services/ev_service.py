# apps/api/src/services/ev_service.py
from typing import Optional

def american_to_decimal(odds: int) -> float:
    if odds > 0:
        return (odds / 100) + 1
    return (100 / abs(odds)) + 1

def decimal_to_implied(decimal_odds: float) -> float:
    return 1 / decimal_odds

def remove_vig(over_odds: int, under_odds: int) -> tuple[float, float]:
    """Remove vig from a two-sided market, return true probabilities."""
    over_implied = decimal_to_implied(american_to_decimal(over_odds))
    under_implied = decimal_to_implied(american_to_decimal(under_odds))
    total_implied = over_implied + under_implied
    true_over = over_implied / total_implied
    true_under = under_implied / total_implied
    return round(true_over, 4), round(true_under, 4)

def calculate_ev(pick: str, odds: int, true_prob: float) -> float:
    """
    EV% = (true_prob * profit) - ((1 - true_prob) * stake)
    Expressed as percentage of stake.
    """
    decimal = american_to_decimal(odds)
    profit = decimal - 1  # profit per $1 staked
    ev = (true_prob * profit) - ((1 - true_prob) * 1)
    return round(ev * 100, 2)

def calculate_kelly(ev: float, odds: int, true_prob: float, fraction: float = 0.25) -> float:
    """
    Full Kelly: (bp - q) / b
    b = decimal odds - 1
    p = true probability of win
    q = 1 - p
    fraction = kelly fraction (0.25 = quarter kelly, safer)
    """
    b = american_to_decimal(odds) - 1
    p = true_prob
    q = 1 - p
    if b <= 0: return 0.0
    kelly = (b * p - q) / b
    return round(max(kelly * fraction, 0) * 100, 2)  # as % of bankroll

def grade_prop(
    pick: str,
    over_odds: int,
    under_odds: int,
    hit_rate: Optional[float] = None,
    model_proj: Optional[float] = None,
    line: Optional[float] = None,
) -> dict:
    """Full prop grading: EV, Kelly, confidence, grade."""
    true_over, true_under = remove_vig(over_odds, under_odds)
    true_prob = true_over if pick.lower() == "over" else true_under
    pick_odds = over_odds if pick.lower() == "over" else under_odds

    ev = calculate_ev(pick, pick_odds, true_prob)
    kelly = calculate_kelly(ev, pick_odds, true_prob)

    # Boost confidence if hit rate and model proj align
    confidence_score = 0
    if ev > 3:
        confidence_score += 2
    elif ev > 1:
        confidence_score += 1

    if hit_rate:
        if hit_rate >= 70:
            confidence_score += 3
        elif hit_rate >= 60:
            confidence_score += 2
        elif hit_rate >= 55:
            confidence_score += 1

    if model_proj and line:
        edge = abs(model_proj - line)
        if edge >= 3:
            confidence_score += 2
        elif edge >= 1.5:
            confidence_score += 1

    if confidence_score >= 5:
        confidence = "HIGH"
        grade = "A"
    elif confidence_score >= 3:
        confidence = "MEDIUM"
        grade = "B"
    else:
        confidence = "LOW"
        grade = "C"

    return {
        "ev_percentage": ev,
        "kelly_pct": kelly,
        "true_probability": round(true_prob * 100, 1),
        "confidence": confidence,
        "grade": grade,
        "confidence_score": confidence_score,
    }
