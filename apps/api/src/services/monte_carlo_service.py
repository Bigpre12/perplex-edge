# apps/api/src/services/monte_carlo_service.py
"""
Monte Carlo Probability Engine — replaces book-implied odds with
simulation-derived true probabilities.

Data flow:
  player_hit_rates (empirical) → Normal-distribution simulation → true_prob
  Cached in Redis/memory for 30 minutes.
"""
import logging
import numpy as np
from typing import Optional
from sqlalchemy import text
from db.session import async_session_maker
from services.cache import cache  # CacheManager singleton (Redis or in-memory)

logger = logging.getLogger(__name__)


class MonteCarloProbabilityEngine:
    """Run Monte Carlo simulations to derive true probability for player props."""

    def __init__(self):
        self.cache_ttl = 1800  # 30 minutes

    # ------------------------------------------------------------------
    # Historical data lookup
    # ------------------------------------------------------------------
    async def get_historical_hit_rate(
        self, player_name: str, market_key: str, line: float
    ) -> float:
        """
        Query the existing ``player_hit_rates`` table (HitRateModel) which
        stores l5/l10/l20 hit-rate columns.  We normalise by mapping
        ``market_key`` → ``stat_type`` (strip the ``player_`` prefix).

        Falls back to ``props_live`` aggregate if no row exists, and
        ultimately to a 0.50 neutral prior.
        """
        stat_type = market_key.replace("player_", "")

        try:
            async with async_session_maker() as session:
                # 1. Try the dedicated Monte Carlo hit-rate table first
                hr_sql = text("""
                    SELECT hit_rate 
                    FROM player_mc_hit_rates 
                    WHERE player_name = :player_name 
                      AND market_key = :market_key 
                      AND line = :line
                    LIMIT 1
                """)
                result = await session.execute(hr_sql, {
                    "player_name": player_name,
                    "market_key": market_key,
                    "line": line
                })
                row = result.scalar_one_or_none()

                if row is not None:
                    return float(row)

                # 2. Fallback: estimate from props_live confidence column
                pl_sql = text("""
                    SELECT AVG(confidence)
                    FROM props_live
                    WHERE player_name = :player_name
                      AND market_key  = :market_key
                      AND confidence IS NOT NULL
                """)
                result2 = await session.execute(pl_sql, {
                    "player_name": player_name,
                    "market_key": market_key,
                })
                avg_conf = result2.scalar_one_or_none()
                if avg_conf is not None and float(avg_conf) > 0:
                    return min(0.99, max(0.01, float(avg_conf)))

        except Exception as e:
            logger.debug("get_historical_hit_rate fallback for %s: %s", player_name, e)

        return 0.50  # neutral prior

    # ------------------------------------------------------------------
    # Line spread estimation
    # ------------------------------------------------------------------
    async def _get_line_spread_std(
        self, player_name: str, market_key: str, line: float
    ) -> float:
        """
        Estimate standard deviation from the spread of lines across
        different bookmakers in ``unified_odds``.  A wider spread signals
        more market uncertainty → higher std_dev.
        """
        try:
            async with async_session_maker() as session:
                sql = text("""
                    SELECT COALESCE(STDDEV(implied_prob), 0)
                    FROM unified_odds
                    WHERE player_name = :player_name
                      AND market_key  = :market_key
                      AND line        = :line
                      AND implied_prob IS NOT NULL
                """)
                result = await session.execute(sql, {
                    "player_name": player_name,
                    "market_key": market_key,
                    "line": line,
                })
                val = result.scalar_one_or_none()
                if val is not None and float(val) > 0:
                    # Scale the book-level stddev into a simulation-ready range
                    return max(0.05, min(0.30, float(val) * 2.0))
        except Exception:
            pass
        return 0.12  # reasonable baseline

    # ------------------------------------------------------------------
    # Core simulation
    # ------------------------------------------------------------------
    async def simulate(
        self,
        player_name: str,
        market_key: str,
        line: float,
        over_under: str,
        n: int = 10_000,
    ) -> float:
        """
        Run *n* simulations drawing from N(μ, σ) where:
          μ = historical hit-rate mean  (from player_hit_rates or fallback)
          σ = book-spread variance      (from unified_odds or baseline)

        Returns ``true_probability`` ∈ (0.01, 0.99).
        """
        cache_key = (
            f"mc:{player_name.replace(' ', '_')}:{market_key}:{line}:{over_under}"
        )

        # Check cache first
        cached = await cache.get(cache_key)
        if cached is not None:
            try:
                return float(cached)
            except (ValueError, TypeError):
                pass

        try:
            hit_rate_mean = await self.get_historical_hit_rate(
                player_name, market_key, line
            )
            std_dev = await self._get_line_spread_std(
                player_name, market_key, line
            )

            # Draw from the distribution
            sims = np.random.normal(loc=hit_rate_mean, scale=std_dev, size=n)

            if over_under.lower() == "over":
                hits = int(np.sum(sims > 0.5))
            else:
                hits = int(np.sum(sims <= 0.5))

            true_prob = max(0.01, min(0.99, hits / n))

            # Write to cache
            await cache.set(cache_key, str(round(true_prob, 6)), ttl=self.cache_ttl)

            return true_prob

        except Exception as e:
            logger.error("Monte Carlo simulation failed for %s: %s", player_name, e)
            return 0.50


# Singleton
monte_carlo_engine = MonteCarloProbabilityEngine()
