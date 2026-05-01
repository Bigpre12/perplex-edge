# apps/api/src/services/brains_service.py
"""
Brains Scorer — the final decision engine.

Combines Monte Carlo true-probability, CLV, and sharp consensus into a
single confidence score, tier, natural-language reason, and recommendation.

No tab should ever display a number that came directly from a book's
implied odds without being processed by at least ONE internal AI engine.
"""
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class BrainsScorer:
    """Weights: MC 50%, CLV 30%, Sharp 20%."""

    # ------------------------------------------------------------------
    # Weight constants
    # ------------------------------------------------------------------
    MC_WEIGHT = 0.50
    CLV_WEIGHT = 0.30
    SHARP_WEIGHT = 0.20

    # ------------------------------------------------------------------
    # Tier thresholds
    # ------------------------------------------------------------------
    # tier S: confidence >= 80 AND edge >= 5%
    # tier A: confidence >= 65 AND edge >= 3%
    # tier B: confidence >= 50 AND edge >= 1%
    # tier C: everything else

    def _tier(self, confidence: float, edge_percent: float) -> str:
        if confidence >= 80 and edge_percent >= 5.0:
            return "S"
        if confidence >= 65 and edge_percent >= 3.0:
            return "A"
        if confidence >= 50 and edge_percent >= 1.0:
            return "B"
        return "C"

    def _recommendation(self, confidence: float, edge_percent: float) -> str:
        """BET / LEAN / WATCH / SKIP."""
        if confidence >= 80 and edge_percent >= 5.0:
            return "BET"
        if confidence >= 65 and edge_percent >= 3.0:
            return "LEAN"
        if confidence >= 50 and edge_percent >= 1.0:
            return "WATCH"
        return "SKIP"

    # ------------------------------------------------------------------
    # Sub-score helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _mc_confidence(monte_carlo_prob: float, implied_prob: float) -> float:
        """
        MC sub-score (0-100).
        Higher when Monte Carlo probability diverges positively from implied.
        A neutral (0.50) MC returns ~50.
        """
        if monte_carlo_prob <= 0 or implied_prob <= 0:
            return 50.0
        edge = (monte_carlo_prob - implied_prob)  # e.g. 0.08
        # Map edge into a 0-100 scale: 0 edge → 50, 0.15+ edge → ~95
        return min(100.0, max(0.0, 50.0 + edge * 300))

    @staticmethod
    def _clv_confidence(clv: float) -> float:
        """
        CLV sub-score (0-100).
        Positive CLV (beating the close) → higher score.
        """
        # clv is in American-odds points, e.g. +15 is great, -10 is bad
        return min(100.0, max(0.0, 50.0 + clv * 2.0))

    @staticmethod
    def _sharp_confidence(steam_signal: bool, sharp_consensus: float) -> float:
        """
        Sharp sub-score (0-100).
        ``sharp_consensus`` = fraction of sharp books agreeing with the side (0-1).
        ``steam_signal`` = True if steam detected.
        """
        base = sharp_consensus * 80.0  # 0-80
        if steam_signal:
            base += 20.0
        return min(100.0, max(0.0, base))

    # ------------------------------------------------------------------
    # Main scoring method
    # ------------------------------------------------------------------
    def score_prop(
        self,
        monte_carlo_prob: float,
        implied_prob: float,
        clv: float = 0.0,
        steam_signal: bool = False,
        sharp_consensus: float = 0.5,
        player_name: str = "Unknown",
        side: str = "over",
        line: float = 0.0,
    ) -> Dict[str, Any]:
        """
        Return the full Brains signal dict:
        {
            "true_prob", "confidence", "tier", "edge_percent",
            "reason", "clv", "steam", "recommendation"
        }
        """
        # Sub-scores
        mc_score = self._mc_confidence(monte_carlo_prob, implied_prob)
        clv_score = self._clv_confidence(clv)
        sharp_score = self._sharp_confidence(steam_signal, sharp_consensus)

        # Weighted confidence (0-100)
        confidence = round(
            mc_score * self.MC_WEIGHT
            + clv_score * self.CLV_WEIGHT
            + sharp_score * self.SHARP_WEIGHT,
            2,
        )

        edge_percent = round((monte_carlo_prob - implied_prob) * 100, 2)
        tier = self._tier(confidence, edge_percent)
        rec = self._recommendation(confidence, edge_percent)

        # Natural-language reason
        sharp_label = "aligned" if sharp_consensus >= 0.6 else "mixed"
        steam_label = "Steam detected." if steam_signal else "No steam."
        clv_label = f"+{clv}" if clv > 0 else str(clv)

        reason = (
            f"{player_name} {side.upper()} {line}: "
            f"Model gives {round(monte_carlo_prob * 100, 1)}% true probability "
            f"vs {round(implied_prob * 100, 1)}% implied. "
            f"CLV: {clv_label}. Sharp consensus: {sharp_label}. {steam_label} "
            f"Confidence: {confidence}/100."
        )

        return {
            "true_prob": round(monte_carlo_prob, 4),
            "confidence": confidence,
            "tier": tier,
            "edge_percent": edge_percent,
            "reason": reason,
            "clv": round(clv, 2),
            "steam": steam_signal,
            "recommendation": rec,
        }


# Singleton
brains_scorer = BrainsScorer()
