# backend/routers/affiliate_router.py
# Deeplinks with affiliate tracking params
from fastapi import APIRouter, Query
from urllib.parse import quote
from typing import Optional
import os

router = APIRouter(prefix='/api/affiliate', tags=['affiliate'])

AFFILIATE_CODES = {
    'draftkings': os.getenv('DK_AFFILIATE_CODE', ''),
    'fanduel':    os.getenv('FD_AFFILIATE_CODE', ''),
    'betmgm':     os.getenv('BETMGM_AFFILIATE_CODE', ''),
    'caesars':    os.getenv('CAESARS_AFFILIATE_CODE', ''),
    'bet365':     os.getenv('BET365_AFFILIATE_CODE', ''),
}

def build_deeplink(book: str, player: str, stat: str, line: float, side: str) -> str:
    code = AFFILIATE_CODES.get(book.lower(), '')
    player_enc = quote(player)
    templates = {
        'draftkings': f'https://sportsbook.draftkings.com/featured-tab?btag={code}',
        'fanduel':    f'https://sportsbook.fanduel.com/sports/playerprops?pid=0&affiliateCode={code}',
        'betmgm':     f'https://sports.betmgm.com/en/sports?btag={code}',
        'caesars':    f'https://sportsbook.caesars.com/us/nj/bet?referral={code}',
        'bet365':     f'https://www.bet365.com/?affiliateCode={code}',
    }
    return templates.get(book.lower(), f'https://{book}.com')

@router.get('/link')
def get_affiliate_link(book: str, player: str = Query(...), stat: str = Query(...),
                        line: float = Query(...), side: str = Query(default='over')):
    url = build_deeplink(book, player, stat, line, side)
    return {'book': book, 'player': player, 'stat': stat, 'line': line, 'side': side, 'url': url}

@router.get('/all-books')
def get_all_book_links(player: str = Query(...), stat: str = Query(...),
                        line: float = Query(...), side: str = Query(default='over')):
    return [{'book': book, 'url': build_deeplink(book, player, stat, line, side)}
            for book in AFFILIATE_CODES.keys()]
