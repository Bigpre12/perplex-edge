"""
Detect 2-way h2h arbitrage from TheOddsAPI event payloads; persist to arbitrage_opportunities.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import DATABASE_URL

logger = logging.getLogger(__name__)


def _american_implied_prob(american: int) -> float:
    if american > 0:
        return 100.0 / (american + 100.0)
    aa = abs(american)
    return float(aa) / (aa + 100.0)


def _scan_event_h2h(sport: str, event: Dict[str, Any]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    eid = event.get("id")
    if not eid or not isinstance(event, dict):
        return out
    # market -> outcome_name -> book -> american odds
    market_map: Dict[str, Dict[str, Dict[str, int]]] = {}
    for bm in event.get("bookmakers") or []:
        book = bm.get("key")
        if not book:
            continue
        for mkt in bm.get("markets") or []:
            mk = mkt.get("key")
            if mk != "h2h":
                continue
            if mk not in market_map:
                market_map[mk] = {}
            for oc in mkt.get("outcomes") or []:
                name = oc.get("name")
                price = oc.get("price")
                if not name or price is None:
                    continue
                try:
                    odds_i = int(price)
                except (TypeError, ValueError):
                    continue
                market_map[mk].setdefault(name, {})[book] = odds_i

    h2h = market_map.get("h2h", {})
    names = list(h2h.keys())
    if len(names) != 2:
        return out
    a_name, b_name = names[0], names[1]
    side_a = h2h.get(a_name, {})
    side_b = h2h.get(b_name, {})

    for book_a, odds_a in side_a.items():
        for book_b, odds_b in side_b.items():
            if book_a == book_b:
                continue
            p_a = _american_implied_prob(odds_a)
            p_b = _american_implied_prob(odds_b)
            total = p_a + p_b
            if total < 1.0 - 1e-9:
                arb_pct = round((1.0 - total) * 100.0, 4)
                profit_per_100 = round((1.0 - total) * 100.0, 2)
                out.append(
                    {
                        "event_id": str(eid),
                        "sport": sport,
                        "market": "h2h",
                        "outcome_a": a_name,
                        "outcome_b": b_name,
                        "book_a": book_a,
                        "book_b": book_b,
                        "odds_a": odds_a,
                        "odds_b": odds_b,
                        "arb_pct": arb_pct,
                        "profit_per_100": profit_per_100,
                    }
                )
    return out


def _prop_parlay_decimal(odds: int) -> float:
    if odds > 0:
        return (odds / 100.0) + 1.0
    return (100.0 / abs(odds)) + 1.0


def _find_totals_arb(over_odds: int, under_odds: int) -> Optional[Dict[str, Any]]:
    over_dec = _prop_parlay_decimal(over_odds)
    under_dec = _prop_parlay_decimal(under_odds)
    inv_sum = (1.0 / over_dec) + (1.0 / under_dec)
    if inv_sum < 1.0 - 1e-9:
        arb_pct = round((1.0 - inv_sum) * 100.0, 4)
        profit_per_100 = round((1.0 - inv_sum) * 100.0, 2)
        return {"arb_pct": arb_pct, "profit_per_100": profit_per_100}
    return None


def _scan_props_arbs(sport: str, props: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for prop in props:
        if not isinstance(prop, dict):
            continue
        overs = prop.get("over") or []
        unders = prop.get("under") or []
        if not overs or not unders:
            continue
        try:
            best_over = max(overs, key=lambda x: int(x.get("odds", -10000)))
            best_under = max(unders, key=lambda x: int(x.get("odds", -10000)))
        except (TypeError, ValueError):
            continue
        if best_over.get("book") == best_under.get("book"):
            continue
        oa = int(best_over.get("odds") or 0)
        ob = int(best_under.get("odds") or 0)
        arb = _find_totals_arb(oa, ob)
        if not arb:
            continue
        player = prop.get("player_name") or "Prop"
        line = prop.get("line") or best_over.get("line") or 0
        eid = prop.get("event_id") or prop.get("game_id") or "unknown"
        mkt = prop.get("market_key") or prop.get("stat_type") or "player_prop"
        out.append(
            {
                "event_id": str(eid),
                "sport": sport,
                "market": str(mkt)[:50],
                "outcome_a": f"{player} OVER {line}",
                "outcome_b": f"{player} UNDER {line}",
                "book_a": str(best_over.get("book") or ""),
                "book_b": str(best_under.get("book") or ""),
                "odds_a": oa,
                "odds_b": ob,
                "arb_pct": arb["arb_pct"],
                "profit_per_100": arb["profit_per_100"],
            }
        )
    return out


async def find_and_store_arb_from_props(
    session: AsyncSession, sport: str, props: List[Dict[str, Any]]
) -> int:
    if not props or "sqlite" in (DATABASE_URL or "").lower():
        return 0
    all_opps = _scan_props_arbs(sport, props)
    if not all_opps:
        return 0
    stmt = text(
        """
        INSERT INTO arbitrage_opportunities (
          event_id, sport, market, outcome_a, outcome_b, book_a, book_b,
          odds_a, odds_b, arb_pct, profit_per_100, detected_at, expires_at
        ) VALUES (
          :event_id, :sport, :market, :outcome_a, :outcome_b, :book_a, :book_b,
          :odds_a, :odds_b, :arb_pct, :profit_per_100, NOW(), NOW() + INTERVAL '20 minutes'
        )
        """
    )
    n = 0
    try:
        for opp in all_opps[:500]:
            await session.execute(stmt, opp)
            n += 1
        await session.commit()
        if n:
            logger.info("arb_calculator: stored %s prop arbs for %s", n, sport)
        return n
    except Exception as e:
        await session.rollback()
        logger.debug("arb_calculator props store skipped: %s", e)
        return 0


async def find_and_store_arbs(session: AsyncSession, sport: str, odds_raw: List[Dict[str, Any]]) -> int:
    if not odds_raw or "sqlite" in (DATABASE_URL or "").lower():
        return 0
    all_opps: List[Dict[str, Any]] = []
    for event in odds_raw:
        if isinstance(event, dict):
            all_opps.extend(_scan_event_h2h(sport, event))
    if not all_opps:
        return 0
    stmt = text(
        """
        INSERT INTO arbitrage_opportunities (
          event_id, sport, market, outcome_a, outcome_b, book_a, book_b,
          odds_a, odds_b, arb_pct, profit_per_100, detected_at, expires_at
        ) VALUES (
          :event_id, :sport, :market, :outcome_a, :outcome_b, :book_a, :book_b,
          :odds_a, :odds_b, :arb_pct, :profit_per_100, NOW(), NOW() + INTERVAL '20 minutes'
        )
        """
    )
    n = 0
    try:
        for opp in all_opps[:500]:
            await session.execute(stmt, opp)
            n += 1
        await session.commit()
        if n:
            logger.info("arb_calculator: stored %s h2h arbs for %s", n, sport)
        return n
    except Exception as e:
        await session.rollback()
        logger.debug("arb_calculator store skipped: %s", e)
        return 0


async def fetch_recent_arbs(session: AsyncSession, sport: Optional[str], limit: int = 50) -> List[Dict[str, Any]]:
    if "sqlite" in (DATABASE_URL or "").lower():
        return []
    try:
        if sport:
            q = text(
                """
                SELECT id, event_id, sport, market, outcome_a, outcome_b, book_a, book_b,
                       odds_a, odds_b, arb_pct, profit_per_100, detected_at, expires_at
                FROM arbitrage_opportunities
                WHERE sport = :sport AND expires_at > NOW()
                ORDER BY arb_pct DESC NULLS LAST, detected_at DESC
                LIMIT :lim
                """
            )
            res = await session.execute(q, {"sport": sport, "lim": limit})
        else:
            q = text(
                """
                SELECT id, event_id, sport, market, outcome_a, outcome_b, book_a, book_b,
                       odds_a, odds_b, arb_pct, profit_per_100, detected_at, expires_at
                FROM arbitrage_opportunities
                WHERE expires_at > NOW()
                ORDER BY arb_pct DESC NULLS LAST, detected_at DESC
                LIMIT :lim
                """
            )
            res = await session.execute(q, {"lim": limit})
        return [dict(r._mapping) for r in res.fetchall()]
    except Exception as e:
        logger.debug("fetch_recent_arbs: %s", e)
        return []
