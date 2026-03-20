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
                last_update = bookmaker.get('last_update')
                source_ts = datetime.fromisoformat(last_update.replace('Z', '+00:00')) if last_update else now
                
                for market in bookmaker.get('markets', []):
                    m_key = market.get('key')
                    
                    for outcome in market.get('outcomes', []):
                        name = outcome.get('name')
                        desc = outcome.get('description') # Player name
                        price = outcome.get('price')
                        line = outcome.get('point')
                        
                        if name is None or price is None: continue
                        
                        # Outcome keys: over, under, home, away, etc.
                        side = name.lower()
                        p_name = desc if m_key not in ['h2h', 'spreads', 'totals'] else None
                        
                        # Composite key for grouping Over/Under
                        group_key = (eid, m_key, p_name or "team", book_key)
                        
                        if group_key not in grouped_data:
                            grouped_data[group_key] = {
                                "sport": sport,
                                "league": league,
                                "game_id": eid,
                                "game_start_time": meta.get('game_time'),
                                "player_name": p_name,
                                "market_key": m_key,
                                "line": Decimal(str(line)) if line is not None else None,
                                "book": book_key,
                                "source_ts": source_ts
                            }
                        
                        implied = self.american_to_implied(int(price)) if isinstance(price, (int, float)) else Decimal('0')
                        
                        if 'over' in side or 'home' in side:
                            grouped_data[group_key]["odds_over"] = Decimal(str(price))
                            grouped_data[group_key]["implied_over"] = implied
                        elif 'under' in side or 'away' in side:
                            grouped_data[group_key]["odds_under"] = Decimal(str(price))
                            grouped_data[group_key]["implied_under"] = implied

        for data in grouped_data.values():
            try:
                records.append(PropRecord(**data))
            except Exception as e:
                logger.error(f"OddsMapper: Validation failed for record {data.get('game_id')}: {e}")

        return records

odds_mapper = OddsMapper()
