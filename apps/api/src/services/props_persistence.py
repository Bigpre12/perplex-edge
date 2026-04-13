# services/props_persistence.py
from datetime import datetime, timezone
from typing import List, Dict, Any
from services.db import db
from services.props_models import PropRecord

def _american_to_implied(odds: int) -> float:
    if odds > 0:
        return 100.0 / (odds + 100.0)
    return abs(odds) / (abs(odds) + 100.0)

def prop_group_to_records(
    grouped_prop: dict,
    sport_key: str,
    league: str,
) -> List[PropRecord]:
    records: List[PropRecord] = []
    player = grouped_prop["player"]
    market = grouped_prop["market"]
    game_id = grouped_prop["game_id"]
    start_time = grouped_prop["start_time"]

    for book_key, b in grouped_prop["books"].items():
        odds_over = int(b["over"])
        odds_under = int(b["under"])

        implied_over = _american_to_implied(odds_over)
        implied_under = _american_to_implied(odds_under)

        rec = PropRecord(
            sport=sport_key,
            league=league,
            game_id=game_id,
            game_start_time=start_time,
            player_id=player["name"],
            player_name=player["name"],
            team=player.get("team") or "",
            market_key=market["stat_type"],
            market_label=market["stat_type"],
            line=float(b["line"]),
            book=book_key,
            odds_over=odds_over,
            odds_under=odds_under,
            implied_over=implied_over,
            implied_under=implied_under,
        )
        records.append(rec)

    return records

def records_to_rows(records: List[PropRecord]) -> List[Dict[str, Any]]:
    now = datetime.now(timezone.utc)
    rows: List[Dict[str, Any]] = []
    for r in records:
        rows.append(
            {
                "sport": r.sport,
                "league": r.league,
                "game_id": r.game_id,
                "game_start_time": r.game_start_time,
                "player_id": r.player_id,
                "player_name": r.player_name,
                "team": r.team,
                "market_key": r.market_key,
                "market_label": r.market_label,
                "line": r.line,
                "book": r.book,
                "odds_over": r.odds_over,
                "odds_under": r.odds_under,
                "implied_over": r.implied_over,
                "implied_under": r.implied_under,
                "last_updated_at": now,
                "snapshot_at": now,
                "source": "live_ingest",
                "run_id": None,
                "is_close": False,
                "is_best_over": r.is_best_over,
                "is_best_under": r.is_best_under,
                "is_soft_book": r.is_soft_book,
                "is_sharp_book": r.is_sharp_book,
                "confidence": r.confidence,
            }
        )
    return rows

async def upsert_props_live(rows: List[Dict[str, Any]]) -> None:
    if not rows:
        return
    query = """
    insert into public.props_live (
      sport, league, game_id, game_start_time,
      player_id, player_name, team,
      market_key, market_label, line,
      book, odds_over, odds_under,
      implied_over, implied_under,
      is_best_over, is_best_under,
      is_soft_book, is_sharp_book,
      confidence, last_updated_at
    )
    values (
      :sport, :league, :game_id, :game_start_time,
      :player_id, :player_name, :team,
      :market_key, :market_label, :line,
      :book, :odds_over, :odds_under,
      :implied_over, :implied_under,
      :is_best_over, :is_best_under,
      :is_soft_book, :is_sharp_book,
      :confidence, :last_updated_at
    )
    on conflict (sport, game_id, player_id, market_key, book)
    do update set
      line = excluded.line,
      odds_over = excluded.odds_over,
      odds_under = excluded.odds_under,
      implied_over = excluded.implied_over,
      implied_under = excluded.implied_under,
      is_best_over = excluded.is_best_over,
      is_best_under = excluded.is_best_under,
      is_soft_book = excluded.is_soft_book,
      is_sharp_book = excluded.is_sharp_book,
      confidence = excluded.confidence,
      last_updated_at = excluded.last_updated_at;
    """
    # Note: Using :param style for SQLAlchemy text() execution in my DBWrapper
    await db.executemany(query, rows)

async def insert_props_history(rows: List[Dict[str, Any]]) -> None:
    if not rows:
        return
    query = """
    insert into public.props_history (
      snapshot_at,
      sport, league, game_id, game_start_time,
      player_id, player_name, team,
      market_key, market_label, line,
      book, odds_over, odds_under,
      implied_over, implied_under,
      source, run_id, is_close,
      is_best_over, is_best_under,
      is_soft_book, is_sharp_book,
      confidence
    )
    values (
      :snapshot_at,
      :sport, :league, :game_id, :game_start_time,
      :player_id, :player_name, :team,
      :market_key, :market_label, :line,
      :book, :odds_over, :odds_under,
      :implied_over, :implied_under,
      :source, :run_id, :is_close,
      :is_best_over, :is_best_under,
      :is_soft_book, :is_sharp_book,
      :confidence
    );
    """
    await db.executemany(query, rows)
