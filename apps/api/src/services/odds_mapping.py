# apps/api/src/services/odds_mapping.py
import logging
import os
from typing import List, Dict, Any
from datetime import datetime, timezone
from decimal import Decimal
from schemas.props import PropRecord

logger = logging.getLogger(__name__)
ODDS_MAPPING_VERBOSE = os.getenv("ODDS_MAPPING_VERBOSE", "false").strip().lower() == "true"
ODDS_MAPPING_VERBOSE_LIMIT = max(0, int(os.getenv("ODDS_MAPPING_VERBOSE_LIMIT", "25")))

class OddsMapper:
    @staticmethod
    def american_to_implied(american: int) -> Decimal:
        if american > 0:
            return Decimal(100) / Decimal(american + 100)
        return Decimal(abs(american)) / Decimal(abs(american) + 100)

    def _normalize_player_name(self, name: str) -> str:
        if not name: return ""
        # 1. Clean whitespace and basic noise
        name = name.strip()
        # 2. Handle "Last, First" -> "First Last"
        if "," in name:
            parts = [p.strip() for p in name.split(",")]
            if len(parts) == 2:
                name = f"{parts[1]} {parts[0]}"
        # 3. Strip Jr/III/etc
        suffixes = [" jr.", " jr", " iii", " ii", " iv"]
        for s in suffixes:
            if name.lower().endswith(s):
                name = name[:-(len(s))].strip()
        
        return name.title()

    def map_theodds_props_to_records(self, odds_raw: List[Dict], metadata_map: Dict, sport: str) -> List[PropRecord]:
        """
        Groups OddsAPI response into consolidated PropRecord rows.
        Groups Over/Under outcomes into a single record per (game, player, market, book).
        """
        logger.debug("OddsMapper: Processing %s raw event entries for %s", len(odds_raw), sport)
        now = datetime.now(timezone.utc)
        records = []
        verbose_count = 0

        def _verbose_log(msg: str, *args) -> None:
            nonlocal verbose_count
            if not ODDS_MAPPING_VERBOSE:
                return
            if verbose_count < ODDS_MAPPING_VERBOSE_LIMIT:
                logger.debug(msg, *args)
                verbose_count += 1
                if verbose_count == ODDS_MAPPING_VERBOSE_LIMIT:
                    logger.debug(
                        "OddsMapper verbose log limit reached (%s); suppressing further per-outcome logs.",
                        ODDS_MAPPING_VERBOSE_LIMIT,
                    )
        
        # Intermediate grouping map: (game_id, market_key, player_name, bookmaker) -> data
        grouped_data = {}
        market_counts: Dict[str, int] = {}
        bookmaker_counts: Dict[str, int] = {}

        for event in odds_raw:
            eid = event.get('id')
            if not eid: continue
            
            meta = metadata_map.get(eid, {})
            league = event.get('sport_title') or sport.split('_')[-1].upper()
            
            for bookmaker in event.get('bookmakers', []):
                book_key = bookmaker.get('key')
                bookmaker_counts[book_key or "unknown"] = bookmaker_counts.get(book_key or "unknown", 0) + 1
                _verbose_log("OddsMapper book=%s event=%s", book_key, eid)
                last_update = bookmaker.get('last_update')
                source_ts = datetime.fromisoformat(last_update.replace('Z', '+00:00')) if last_update else now
                
                for market in bookmaker.get('markets', []):
                    m_key = market.get('key')
                    market_counts[m_key or "unknown"] = market_counts.get(m_key or "unknown", 0) + 1
                    _verbose_log("OddsMapper market=%s book=%s event=%s", m_key, book_key, eid)
                    
                    for outcome in market.get('outcomes', []):
                        name = outcome.get('name')
                        desc = outcome.get('description') # Player name
                        price = outcome.get('price')
                        line = outcome.get('point')
                        _verbose_log(
                            "OddsMapper outcome name=%s desc=%s price=%s line=%s market=%s",
                            name,
                            desc,
                            price,
                            line,
                            m_key,
                        )
                        
                        if name is None or price is None: continue

                        # NBA Spread Protection: skip anomalous lines
                        if m_key == "spreads" and line is not None and abs(float(line)) > 20.0:
                            logger.warning(f"OddsMapper: Rejected bad spread line {line} from {book_key}")
                            continue
                        
                        # Outcome keys: over, under, home, away, etc.
                        side = name.lower()
                        
                        # Robust player name extraction: 
                        # In Player Props, name is often 'Over'/'Under' and description is the player name.
                        # However, some books reverse this or put the name in the 'name' field for H2H.
                        is_main_market = m_key in ['h2h', 'spreads', 'totals']
                        p_name = ""
                        if not is_main_market:
                            # Prefer description, then name if description is 'Over'/'Under'
                            p_name = desc if desc else ""
                            if p_name.lower() in ['over', 'under'] and name:
                                p_name = name
                        
                        if not p_name and not is_main_market:
                             p_name = desc or name or ""

                        # Clean up p_name from common noise
                        p_name = self._normalize_player_name(p_name)
                        if p_name.lower() in ['over', 'under', 'yes', 'no']:
                            p_name = ""
                        
                        # Composite key for grouping Over/Under
                        group_key = (eid, m_key, p_name or "team", book_key)
                        
                        if group_key not in grouped_data:
                            _verbose_log("OddsMapper new_group_key=%s", group_key)
                            grouped_data[group_key] = {
                                "sport": sport,
                                "league": league,
                                "game_id": eid,
                                "game_start_time": meta.get('game_time'),
                                "home_team": meta.get('home_team'),
                                "away_team": meta.get('away_team'),
                                "player_name": p_name,
                                "market_key": m_key,
                                "line": Decimal(str(line)) if line is not None else None,
                                "book": book_key,
                                "source_ts": source_ts,
                                "odds_over": None,
                                "odds_under": None,
                                "implied_over": None,
                                "implied_under": None
                            }
                        
                        implied = self.american_to_implied(int(price)) if isinstance(price, (int, float)) else Decimal('0')
                        _verbose_log("OddsMapper side=%s implied=%s", side, implied)
                        
                        # Better H2H/Main mapping: 'Home' -> Over slot, 'Away' -> Under slot
                        is_home = 'over' in side or 'home' in side or side == (meta.get('home_team') or "").lower()
                        is_away = 'under' in side or 'away' in side or side == (meta.get('away_team') or "").lower()

                        if is_home:
                            grouped_data[group_key]["odds_over"] = Decimal(str(price))
                            grouped_data[group_key]["implied_over"] = implied
                        elif is_away:
                            grouped_data[group_key]["odds_under"] = Decimal(str(price))
                            grouped_data[group_key]["implied_under"] = implied
                        else:
                            # Robust fallback for H2H if meta name mapping failed
                            if m_key == 'h2h':
                                if grouped_data[group_key]["odds_over"] is None:
                                    grouped_data[group_key]["odds_over"] = Decimal(str(price))
                                    grouped_data[group_key]["implied_over"] = implied
                                elif grouped_data[group_key]["odds_under"] is None:
                                    grouped_data[group_key]["odds_under"] = Decimal(str(price))
                                    grouped_data[group_key]["implied_under"] = implied
 
        logger.info(
            "OddsMapper summary sport=%s grouped=%s markets=%s books=%s",
            sport,
            len(grouped_data),
            market_counts,
            bookmaker_counts,
        )
        for data in grouped_data.values():
            try:
                records.append(PropRecord(**data))
            except Exception as e:
                logger.error(f"OddsMapper: Validation failed for record {data.get('game_id')}: {e}")

        return records

odds_mapper = OddsMapper()
