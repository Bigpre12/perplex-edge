import logging
import httpx
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, List, Any
from sqlalchemy import select, update
from db.session import async_session_maker
from models.brain import ModelPick
from services.espn_client import espn_client

logger = logging.getLogger(__name__)


class InvalidEspnEventIdError(Exception):
    pass

STAT_TYPE_MAP = {
    "player_points": ["points", "pts"],
    "points": ["points", "pts"],
    "player_rebounds": ["rebounds", "reb"],
    "rebounds": ["rebounds", "reb"],
    "player_assists": ["assists", "ast"],
    "assists": ["assists", "ast"],
    "player_threes": ["threePointFieldGoalsMade", "3pm", "3pt"],
    "threes": ["threePointFieldGoalsMade", "3pm", "3pt"],
    "player_steals": ["steals", "stl"],
    "steals": ["steals", "stl"],
    "player_blocks": ["blocks", "blk"],
    "blocks": ["blocks", "blk"],
    "player_turnovers": ["turnovers", "to"],
    "turnovers": ["turnovers", "to"],
    "pitcher_strikeouts": ["strikeouts", "k"],
    "batter_hits": ["hits", "h"],
    "player_pass_yds": ["passingYards", "yds"],
    "player_rush_yds": ["rushingYards", "yds"],
    "player_pass_tds": ["passingTouchdowns", "td"],
    "player_rush_tds": ["rushingTouchdowns", "td"],
    "player_ints": ["interceptions", "int"],
    "player_points_rebounds_assists": ["pra"],
    "player_points_rebounds": ["pr"],
    "player_points_assists": ["pa"],
    "player_rebounds_assists": ["ra"],
}

ESPN_SPORT_MAP = {
    "basketball_nba": ("basketball", "nba"),
    "americanfootball_nfl": ("football", "nfl"),
    "icehockey_nhl": ("hockey", "nhl"),
    "baseball_mlb": ("baseball", "mlb"),
}


class GradingService:
    """
    Auto-Grading Settlement Engine.
    Monitors active picks and settles them once games are completed.
    Uses ESPN box score data for real stat-based settlement.
    """

    def __init__(self) -> None:
        self._invalid_espn_event_ids: Dict[str, set[str]] = {}

    def _mark_invalid_event_id(self, sport_key: str, event_id: str) -> None:
        self._invalid_espn_event_ids.setdefault(sport_key, set()).add(str(event_id))

    def _is_invalid_event_id(self, sport_key: str, event_id: str) -> bool:
        return str(event_id) in self._invalid_espn_event_ids.get(sport_key, set())

    async def _fetch_box_score(self, sport_key: str, game_id: str) -> Optional[Dict[str, Any]]:
        """Fetch ESPN box score for a completed game."""
        if self._is_invalid_event_id(sport_key, game_id):
            return None
        mapping = ESPN_SPORT_MAP.get(sport_key)
        if not mapping:
            return None
        sport, league = mapping
        url = f"https://site.api.espn.com/apis/site/v2/sports/{sport}/{league}/summary?event={game_id}"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(url)
                if resp.status_code == 400:
                    raise InvalidEspnEventIdError(
                        f"ESPN summary rejected event_id={game_id} for sport={sport_key}"
                    )
                resp.raise_for_status()
                return resp.json()
        except InvalidEspnEventIdError:
            raise
        except httpx.HTTPStatusError as e:
            logger.warning("ESPN box score fetch failed for %s: %s", game_id, e)
            return None
        except Exception as e:
            logger.warning(f"ESPN box score fetch failed for {game_id}: {e}")
            return None

    async def _fetch_box_score_with_refresh(
        self,
        sport_key: str,
        game_id: str,
        game_map: Dict[str, Dict[str, Any]],
    ) -> Optional[Dict[str, Any]]:
        """
        Attempt summary fetch once; on 400, force-refresh scoreboard IDs and retry once.
        If still invalid/missing, mark event ID bad to avoid repeated non-transient retries.
        """
        gid = str(game_id)
        try:
            return await self._fetch_box_score(sport_key, gid)
        except InvalidEspnEventIdError:
            logger.warning(
                "ESPN returned 400 for event_id=%s (%s). Refreshing scoreboard IDs and retrying once.",
                gid,
                sport_key,
            )
            fresh_games = await espn_client.get_scoreboard(sport_key, force_refresh=True)
            game_map.clear()
            game_map.update({str(g["id"]): g for g in fresh_games if g.get("id") is not None})
            if gid not in game_map:
                self._mark_invalid_event_id(sport_key, gid)
                logger.warning(
                    "Dropping stale ESPN event_id=%s for %s; not present in refreshed scoreboard IDs.",
                    gid,
                    sport_key,
                )
                return None
            try:
                return await self._fetch_box_score(sport_key, gid)
            except InvalidEspnEventIdError:
                self._mark_invalid_event_id(sport_key, gid)
                logger.warning(
                    "Dropping ESPN event_id=%s for %s after refresh+retry still returned 400.",
                    gid,
                    sport_key,
                )
                return None

    def _extract_player_stat(self, box_score: Dict, player_name: str, stat_type: str) -> Optional[float]:
        """Extract a specific stat value for a player from ESPN box score data."""
        target_keys = STAT_TYPE_MAP.get(stat_type, [stat_type])

        # Combo stats
        combo_parts = {
            "pra": ["points", "rebounds", "assists", "pts", "reb", "ast"],
            "pr": ["points", "rebounds", "pts", "reb"],
            "pa": ["points", "assists", "pts", "ast"],
            "ra": ["rebounds", "assists", "reb", "ast"],
        }

        # Normalize target keys to includes abbreviations
        if any(k in combo_parts for k in target_keys):
            all_parts = []
            for k in target_keys:
                all_parts.extend(combo_parts.get(k, [k]))
            target_stats = list(set(all_parts))
        else:
            target_stats = target_keys

        player_lower = player_name.lower().strip() if player_name else ""

        for team_data in box_score.get("boxscore", {}).get("players", []):
            for stat_group in team_data.get("statistics", []):
                stat_labels = [l.lower() for l in stat_group.get("labels", [])]
                for athlete in stat_group.get("athletes", []):
                    a_name = athlete.get("athlete", {}).get("displayName", "").lower().strip()
                    short_name = athlete.get("athlete", {}).get("shortName", "").lower().strip()
                    # Skip Antigravity Test row
                    if "antigravity" in a_name:
                        continue
                        
                    if player_lower not in a_name and player_lower not in short_name and a_name not in player_lower:
                        continue

                    stats_values = athlete.get("stats", [])
                    total = 0.0
                    found_any = False
                    
                    for target in target_stats:
                        t_lower = target.lower()
                        for idx, label in enumerate(stat_labels):
                            # Exact match or common abbreviation match
                            if t_lower == label or (len(t_lower) > 2 and t_lower in label) or (len(label) > 2 and label in t_lower):
                                if idx < len(stats_values):
                                    try:
                                        val = stats_values[idx]
                                        total += float(val.split("/")[0] if "/" in str(val) else val)
                                        found_any = True
                                    except (ValueError, TypeError):
                                        pass
                                break
                    if found_any:
                        return total
        return None

    async def run_grading_cycle(self):
        """Main entry point for the scheduler."""
        async with async_session_maker() as session:
            try:
                # 0. Cleanup: Reset "ghost" graded picks that have no actual value
                # This allows them to be re-processed by the improved matching logic.
                cleanup_stmt = (
                    update(ModelPick)
                    .where(ModelPick.status.in_(['graded', 'settled']))
                    .where(ModelPick.actual_value == None)
                    .values(status='active')
                )
                await session.execute(cleanup_stmt)
                await session.commit()

                stmt = select(ModelPick).where(ModelPick.status == 'active')
                res = await session.execute(stmt)
                active_picks = res.scalars().all()

                if not active_picks:
                    return

                sports = set(p.sport_key for p in active_picks)
                total_checked = 0
                settled_count = 0
                missing_scores_count = 0

                for sport in sports:
                    games = await espn_client.get_scoreboard(sport)
                    # ESPN IDs are integers stringified in our scoreboard
                    game_map = {str(g['id']): g for g in games}
                    sport_picks = [p for p in active_picks if p.sport_key == sport]

                    # Map for resolving TOA IDs to ESPN IDs
                    toa_to_espn_map: Dict[str, str] = {}
                    
                    # Fetch live_scores to get team names for TOA IDs
                    from sqlalchemy import text
                    ls_res = await session.execute(
                        text("SELECT event_id, home_team, away_team FROM live_scores WHERE sport = :s"),
                        {"s": sport}
                    )
                    ls_data = {r[0]: (r[1], r[2]) for r in ls_res}

                    box_cache: Dict[str, Optional[Dict]] = {}

                    for pick in sport_picks:
                        total_checked += 1
                        gid = str(pick.game_id)
                        
                        # 1. Try direct ID match (if pick already has ESPN ID)
                        game = game_map.get(gid)
                        
                        # 2. Try fuzzy match via live_scores if no direct match
                        if not game and gid in ls_data:
                            h, a = ls_data[gid]
                            h_lower, a_lower = h.lower(), a.lower()
                            for g in games:
                                gh, ga = g['home_team_name'].lower(), g['away_team_name'].lower()
                                # Check if teams match (handle name variations like "Lakers" vs "LA Lakers")
                                if (h_lower in gh or gh in h_lower) and (a_lower in ga or ga in a_lower):
                                    game = g
                                    toa_to_espn_map[gid] = str(g['id'])
                                    break
                        
                        is_over = False
                        if game:
                            is_over = game.get('status') in ('STATUS_FINAL', 'STATUS_POSTPONED', 'STATUS_CANCELED')
                        else:
                            # Fallback for old picks: check if created > 12h ago
                            is_over = datetime.now(timezone.utc) - pick.created_at > timedelta(hours=12)

                        if is_over:
                            # Use resolved ESPN ID if available, otherwise fallback to original ID
                            espn_id = toa_to_espn_map.get(gid, gid)
                            
                            if self._is_invalid_event_id(sport, espn_id):
                                continue
                            if espn_id not in box_cache:
                                box_cache[espn_id] = await self._fetch_box_score_with_refresh(sport, espn_id, game_map)
                            
                            settled = await self.settle_pick(pick, session, box_score=box_cache.get(espn_id))
                            if settled:
                                settled_count += 1
                            else:
                                missing_scores_count += 1
                                
                logger.info(f"📊 [Grader Summary] Checked: {total_checked}, Settled: {settled_count}, Missing: {missing_scores_count}")

            except Exception as e:
                logger.error(f"Grading cycle error: {e}")

    async def settle_pick(self, pick: ModelPick, session, box_score: Optional[Dict] = None) -> bool:
        """Settles a single pick using real ESPN box score stats."""
        try:
            actual_value: Optional[float] = None
            if box_score and pick.player_name and pick.stat_type:
                actual_value = self._extract_player_stat(box_score, pick.player_name, pick.stat_type)

            if actual_value is None:
                logger.debug(f"🔍 [Grader] No score found for {pick.player_name} ({pick.stat_type}) in game {pick.game_id}")
                return False

            if pick.line is None:
                logger.warning(f"⚠️ [Grader] Pick {pick.id} has no line value. Skipping.")
                return False

            side = (pick.side or "over").lower()
            if side == "over":
                was_won = actual_value > pick.line
            else:
                was_won = actual_value < pick.line

            pick.status = 'settled'
            pick.won = was_won
            pick.actual_value = actual_value
            
            # Profit/Loss calculation using American Odds
            # 1.0 unit stake
            odds = pick.odds or -110.0
            if was_won:
                if odds < 0:
                    pick.profit_loss = 100.0 / abs(odds)
                else:
                    pick.profit_loss = odds / 100.0
            else:
                pick.profit_loss = -1.0
                
            pick.updated_at = datetime.now(timezone.utc)

            session.add(pick)
            await session.commit()
            
            result_label = "WIN" if was_won else "LOSS"
            logger.info(f"✅ [Graded] Pick {pick.id}: {pick.player_name} {pick.stat_type} {side.upper()} {pick.line} | Actual: {actual_value} -> {result_label} (P/L: {pick.profit_loss:.2f})")
            return True

    async def grade_recent_props(self, sport: Optional[str] = None) -> List[Dict]:
        """Grade all active picks for a sport (or all sports). Called by POST /api/props/grade."""
        results: List[Dict] = []
        async with async_session_maker() as session:
            try:
                stmt = select(ModelPick).where(ModelPick.status == 'active')
                if sport and sport != "all":
                    stmt = stmt.where(ModelPick.sport_key == sport)

                res = await session.execute(stmt)
                active_picks = res.scalars().all()

                if not active_picks:
                    return results

                sports = set(p.sport_key for p in active_picks)
                for s in sports:
                    games = await espn_client.get_scoreboard(s)
                    game_map = {str(g['id']): g for g in games}
                    
                    # Map for resolving TOA IDs to ESPN IDs
                    toa_to_espn_map: Dict[str, str] = {}
                    
                    # Fetch live_scores to get team names for TOA IDs
                    from sqlalchemy import text
                    ls_res = await session.execute(
                        text("SELECT event_id, home_team, away_team FROM live_scores WHERE sport = :s"),
                        {"s": s}
                    )
                    ls_data = {r[0]: (r[1], r[2]) for r in ls_res}

                    box_cache: Dict[str, Optional[Dict]] = {}

                    for pick in [p for p in active_picks if p.sport_key == s]:
                        gid = str(pick.game_id)
                        
                        # 1. Try direct ID match
                        game = game_map.get(gid)
                        
                        # 2. Try fuzzy match
                        if not game and gid in ls_data:
                            h, a = ls_data[gid]
                            h_lower, a_lower = h.lower(), a.lower()
                            for g in games:
                                gh, ga = g['home_team_name'].lower(), g['away_team_name'].lower()
                                if (h_lower in gh or gh in h_lower) and (a_lower in ga or ga in a_lower):
                                    game = g
                                    toa_to_espn_map[gid] = str(g['id'])
                                    break

                        is_over = False
                        if game:
                            is_over = game.get('status') in ('STATUS_FINAL', 'STATUS_POSTPONED', 'STATUS_CANCELED')
                        else:
                            is_over = datetime.now(timezone.utc) - pick.created_at > timedelta(hours=12)

                        if is_over:
                            espn_id = toa_to_espn_map.get(gid, gid)
                            if self._is_invalid_event_id(s, espn_id):
                                continue
                            if espn_id not in box_cache:
                                box_cache[espn_id] = await self._fetch_box_score_with_refresh(s, espn_id, game_map)
                            
                            settled = await self.settle_pick(pick, session, box_score=box_cache.get(espn_id))
                            if settled:
                                results.append({"pick_id": pick.id, "player": pick.player_name, "status": "settled"})
            except Exception as e:
                logger.error(f"grade_recent_props error: {e}")
        return results


grading_service = GradingService()
