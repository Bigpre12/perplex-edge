# apps/api/src/services/odds_mapping.py
import logging
from typing import List, Dict, Any
from datetime import datetime, timezone
from decimal import Decimal
from schemas.props import PropRecord

logger = logging.getLogger(__name__)

class OddsMapper:
    @staticmethod
    def american_to_implied(american: int) -> Decimal:
        if american > 0:
            return Decimal(100) / Decimal(american + 100)
        return Decimal(abs(american)) / Decimal(abs(american) + 100)

    def map_theodds_props_to_records(self, odds_raw: List[Dict], metadata_map: Dict, sport: str) -> List[PropRecord]:
        """
        Groups OddsAPI response into consolidated PropRecord rows.
        Groups Over/Under outcomes into a single record per (game, player, market, book).
        """
        logger.info(f"OddsMapper: Processing {len(odds_raw)} raw event entries for {sport}")
        now = datetime.now(timezone.utc)
        records = []
        
        # Intermediate grouping map: (game_id, market_key, player_name, bookmaker) -> data
        grouped_data = {}

        for event in odds_raw:
            eid = event.get('id')
            if not eid: continue
            
            meta = metadata_map.get(eid, {})
            league = event.get('sport_title') or sport.split('_')[-1].upper()
            
            for bookmaker in event.get('bookmakers', []):
                book_key = bookmaker.get('key')
                logger.info(f"  Bookmaker: {book_key}")
                last_update = bookmaker.get('last_update')
                source_ts = datetime.fromisoformat(last_update.replace('Z', '+00:00')) if last_update else now
                
                for market in bookmaker.get('markets', []):
                    m_key = market.get('key')
                    logger.info(f"    Market: {m_key}")
                    
                    for outcome in market.get('outcomes', []):
                        name = outcome.get('name')
                        desc = outcome.get('description') # Player name
                        price = outcome.get('price')
                        line = outcome.get('point')
                        logger.info(f"      Outcome: {name} | {desc} | {price} | {line}")
                        
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
                        if p_name.lower() in ['over', 'under', 'yes', 'no']:
                            p_name = ""
                        
                        # Composite key for grouping Over/Under
                        group_key = (eid, m_key, p_name or "team", book_key)
                        
                        if group_key not in grouped_data:
                            print(f"DEBUG: New group key created: {group_key}")
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
                        print(f"DEBUG: Outcome side={side}, implied={implied}")
                        
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
 
        print(f"DEBUG: Final grouped_data count: {len(grouped_data)}")
        for data in grouped_data.values():
            try:
                records.append(PropRecord(**data))
            except Exception as e:
                logger.error(f"OddsMapper: Validation failed for record {data.get('game_id')}: {e}")

        return records

odds_mapper = OddsMapper()
