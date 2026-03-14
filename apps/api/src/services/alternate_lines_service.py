# backend/services/alternate_lines_service.py
# Pulls alternate lines from The Odds API and stores in PropOdds with alt_line=True
import httpx, os
from datetime import datetime
from database import SessionLocal
from models import PropOdds

from app.services.odds_api_client import odds_api

async def fetch_alt_lines(sport: str):
    skey = SPORT_KEYS.get(sport)
    markets = ','.join(ALT_MARKETS.get(sport, []))
    if not skey or not markets:
        return []
    return await odds_api.get_live_odds(skey, markets=markets)

def upsert_alt_prop(db, player_name, sport, stat_category, line, over_odds, under_odds, book):
    existing = db.query(PropOdds).filter(
        PropOdds.player_name == player_name,
        PropOdds.stat_category == stat_category,
        PropOdds.line == line,
        PropOdds.book == book,
        PropOdds.is_alternate == True
    ).first()
    if existing:
        existing.over_odds = over_odds; existing.under_odds = under_odds
        existing.updated_at = datetime.utcnow()
    else:
        db.add(PropOdds(player_name=player_name, sport=sport, stat_category=stat_category,
                         line=line, over_odds=over_odds, under_odds=under_odds,
                         book=book, is_alternate=True, updated_at=datetime.utcnow()))

async def sync_alt_lines(sport: str):
    db = SessionLocal()
    try:
        games = await fetch_alt_lines(sport)
        count = 0
        for game in games:
            for bookmaker in game.get('bookmakers', []):
                book = bookmaker['key']
                for market in bookmaker.get('markets', []):
                    stat_raw = market['key'].replace('player_','').replace('_alternate','')
                    for outcome in market.get('outcomes', []):
                        if outcome.get('point') is None:
                            continue
                        player = outcome['description']
                        side = outcome['name'].lower()
                        line = float(outcome['point'])
                        odds = int(outcome['price'])
                        if side == 'over':
                            upsert_alt_prop(db, player, sport, stat_raw, line, odds, None, book)
                        else:
                            upsert_alt_prop(db, player, sport, stat_raw, line, None, odds, book)
                        count += 1
        db.commit()
        return count
    finally:
        db.close()
