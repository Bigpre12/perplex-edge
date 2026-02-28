# backend/app/antigravity_engine.py
from typing import List, Dict, Any
from app.antigravity_edge_config import get_edge_config
import logging

logger = logging.getLogger(__name__)


def calculate_kelly(model_prob: float, odds: int, fraction: float = 0.25) -> float:
    """Quarter-Kelly stake sizing."""
    if odds > 0:
        b = odds / 100
    else:
        b = 100 / abs(odds)
    q = 1 - model_prob
    kelly = (b * model_prob - q) / b
    return round(max(0.0, kelly * fraction), 4)


def american_to_implied(odds: int) -> float:
    if odds > 0:
        return 100 / (odds + 100)
    return abs(odds) / (abs(odds) + 100)


async def apply_antigravity_filter(raw_picks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Run raw model picks through the antigravity edge config filters.
    Returns only picks that pass all thresholds, with Kelly sizing appended.
    """
    cfg = await get_edge_config()
    passed = []

    for pick in raw_picks:
        try:
            sport_id = pick.get("sport_id") or pick.get("sportid", 0)
            ev = float(pick.get("edge") or pick.get("expected_value") or pick.get("evpercentage", 0))
            confidence = float(pick.get("confidence_score") or pick.get("confidencescore", 0))
            odds = int(pick.get("odds", -110))
            line = float(pick.get("line_value") or pick.get("linevalue", 0))
            model_prob = float(pick.get("model_probability") or pick.get("modelprobability", 0.5))

            # Filter checks
            if sport_id not in cfg.enabled_sports:
                continue
            if not (cfg.min_ev_threshold <= ev <= cfg.max_ev_threshold):
                continue
            if confidence < cfg.min_confidence:
                continue
            if not (cfg.min_odds <= odds <= cfg.max_odds):
                continue
            if not (cfg.min_line_value <= line <= cfg.max_line_value):
                continue

            # Enrich with antigravity fields
            implied_prob = american_to_implied(odds)
            kelly = calculate_kelly(model_prob, odds, cfg.kelly_fraction)
            display_edge = min(ev, cfg.max_edge_percent)
            
            # Sharp flag is True if DB scout flagged it OR if confidence is extremely high
            db_sharp = pick.get("sharp_money", False)
            sharp_flag = db_sharp or (model_prob >= cfg.sharp_money_threshold)

            pick["display_edge"] = display_edge
            pick["kelly_units"] = kelly
            pick["implied_probability"] = round(implied_prob, 4)
            pick["sharp_money"] = sharp_flag
            pick["edge_model"] = cfg.active_edge_model

            passed.append(pick)

        except Exception as e:
            logger.warning(f"Antigravity filter error on pick: {e}")
            continue

    # Sort by EV descending
    passed.sort(key=lambda x: x.get("display_edge", 0), reverse=True)
    return passed
