# apps/api/src/services/results_grader.py
import os
import httpx
import logging
from datetime import datetime, timezone, timedelta
from sqlalchemy import text
from db.session import async_session_maker
from services.prizepicks_collector import normalize_player_name

logger = logging.getLogger(__name__)

BALLDONTLIE_API_KEY = os.getenv("BALLDONTLIE_API_KEY")

def extract_stat_value(stat_row, stat_type):
    """
    Extract a specific stat value from a BallDontLie stat record.
    Maps PrizePicks stat labels to BDL keys.
    """
    if not stat_row:
        return None
        
    st = stat_type.lower()
    
    # Simple stats
    if st in ["points", "pts"]: return stat_row.get("pts")
    if st in ["rebounds", "rebs", "reb"]: return stat_row.get("reb")
    if st in ["assists", "asts", "ast"]: return stat_row.get("ast")
    if st in ["steals", "stls", "stl"]: return stat_row.get("stl")
    if st in ["blocks", "blks", "blk"]: return stat_row.get("blk")
    if st in ["turnovers", "tov"]: return stat_row.get("turnover")
    if st in ["3-pt made", "3pt made", "fg3m"]: return stat_row.get("fg3m")
    if st in ["free throws made", "ftm"]: return stat_row.get("ftm")
    
    # Composed stats
    if "pts+rebs+asts" in st or "pts+reb+ast" in st:
        return (stat_row.get("pts") or 0) + (stat_row.get("reb") or 0) + (stat_row.get("ast") or 0)
    if "pts+rebs" in st or "pts+reb" in st:
        return (stat_row.get("pts") or 0) + (stat_row.get("reb") or 0)
    if "pts+asts" in st or "pts+ast" in st:
        return (stat_row.get("pts") or 0) + (stat_row.get("ast") or 0)
    if "rebs+asts" in st or "reb+ast" in st:
        return (stat_row.get("reb") or 0) + (stat_row.get("ast") or 0)
    
    return None

async def fetch_balldontlie_stats(target_date: str):
    """
    Fetch all player stats for a specific date from BallDontLie v3.
    target_date format: YYYY-MM-DD
    """
    if not BALLDONTLIE_API_KEY:
        logger.warning("BALLDONTLIE_API_KEY not set. Skipping grading.")
        return []

    url = "https://api.balldontlie.io/v3/stats"
    headers = {"Authorization": BALLDONTLIE_API_KEY}
    # BallDontLie v3 uses dates[] array parameter
    params = {"dates[]": target_date, "per_page": 100}
    
    all_stats = []
    cursor = None
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        while True:
            if cursor:
                params["cursor"] = cursor
            
            try:
                resp = await client.get(url, headers=headers, params=params)
                if resp.status_code == 401:
                    logger.error("BallDontLie API: Unauthorized. Check BALLDONTLIE_API_KEY.")
                    break
                resp.raise_for_status()
                data = resp.json()
                
                batch = data.get("data", [])
                all_stats.extend(batch)
                
                meta = data.get("meta", {})
                cursor = meta.get("next_cursor")
                if not cursor or not batch:
                    break
            except Exception as e:
                logger.error(f"BallDontLie API error on date {target_date}: {e}")
                break
                
    return all_stats

async def grade_pending_projections():
    """
    Find ungraded projections from staging, fetch results, and update records.
    """
    async with async_session_maker() as session:
        # 1. Fetch ungraded rows where game time has passed (+ 6 hour buffer for game completion)
        sql = text("""
            SELECT id, player_name, stat_type, line_score, game_time
            FROM pp_projections_staging
            WHERE graded = FALSE 
              AND game_time < (CURRENT_TIMESTAMP - INTERVAL '6 hours')
            ORDER BY game_time ASC
            LIMIT 500
        """)
        result = await session.execute(sql)
        rows = result.fetchall()
        
        if not rows:
            logger.info("Results Grader: No pending projections to grade.")
            return

        # 2. Group by date to minimize API calls
        by_date = {}
        for r in rows:
            if not r.game_time:
                continue
            d_str = r.game_time.date().isoformat()
            if d_str not in by_date:
                by_date[d_str] = []
            by_date[d_str].append(r)

        # 3. Process each date
        graded_count = 0
        for d_str, projections in by_date.items():
            logger.info(f"Results Grader: Fetching BDL stats for {d_str}...")
            stats = await fetch_balldontlie_stats(d_str)
            
            if not stats:
                logger.warning(f"Results Grader: No stats found for {d_str} from BDL.")
                continue
                
            # Create a lookup map: normalized_name -> stat_dict
            stats_map = {}
            for s in stats:
                player = s.get("player", {})
                first = player.get("first_name", "")
                last = player.get("last_name", "")
                norm_name = normalize_player_name(f"{first} {last}")
                # If player appears multiple times (rare but possible), take the one with most stats
                if norm_name not in stats_map or (s.get("pts", 0) > stats_map[norm_name].get("pts", 0)):
                    stats_map[norm_name] = s

            # 4. Grade each projection
            for proj in projections:
                norm_proj_name = normalize_player_name(proj.player_name)
                stat_row = stats_map.get(norm_proj_name)
                
                if not stat_row:
                    continue

                actual_val = extract_stat_value(stat_row, proj.stat_type)
                if actual_val is None:
                    continue

                hit = float(actual_val) >= float(proj.line_score)
                
                # 5. Update DB
                update_sql = text("""
                    UPDATE pp_projections_staging
                    SET graded = TRUE,
                        actual_value = :actual_value,
                        hit = :hit
                    WHERE id = :id
                """)
                await session.execute(update_sql, {
                    "id": proj.id,
                    "actual_value": float(actual_val),
                    "hit": hit
                })
                graded_count += 1
                logger.info(f"Graded {proj.player_name} ({proj.stat_type}): {actual_val} vs {proj.line_score} -> HIT={hit}")

        await session.commit()
        logger.info(f"Results Grader: Finished grading {graded_count} projections.")

async def run_grader():
    """Entry point for the grader task."""
    logger.info("Results Grader: Starting grading cycle...")
    await grade_pending_projections()
