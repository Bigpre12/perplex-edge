# backend/services/discord_bot.py
# Daily digest bot — posts top picks to Discord at 11am CST
import httpx, os, asyncio
from datetime import datetime
from sqlalchemy.orm import Session
from database import SessionLocal
from models import PropLine

DISCORD_WEBHOOK = os.getenv('DISCORD_WEBHOOK_URL')

def build_digest_embed(db: Session) -> dict:
    top_props = db.query(PropLine).filter(
        PropLine.confidence_score >= 60
    ).order_by(PropLine.confidence_score.desc()).limit(5).all()
    if not top_props:
        return None
    fields = []
    for i, p in enumerate(top_props, 1):
        ev = getattr(p, 'ev_pct', 'N/A')
        dvp = getattr(p, 'dvp_label', 'N/A')
        hr = getattr(p, 'hit_rate_l10', 'N/A')
        conf = getattr(p, 'confidence_score', 'N/A')
        fields.append({
            'name': f'{i}. {p.player_name} ({p.sport})',
            'value': f'**{p.stat_category} OVER {p.line}**\nConf: {conf}/100 | L10: {hr}% | DvP: {dvp} | EV: {ev}%',
            'inline': False
        })
    return {
        'username': 'LOLA',
        'avatar_url': 'https://yourdomain.com/icons/icon-192.png',
        'embeds': [{
            'title': f'LOLA Top Picks — {datetime.utcnow().strftime("%b %d, %Y")}',
            'description': 'Your daily AI-graded prop picks. Confidence 60+.',
            'color': 3447003,
            'fields': fields,
            'footer': {'text': 'LOLA Sports Betting Analytics | lola.yourdomain.com'},
            'timestamp': datetime.utcnow().isoformat()
        }]
    }

async def send_daily_digest():
    if not DISCORD_WEBHOOK:
        print('No Discord webhook set')
        return
    db = SessionLocal()
    try:
        embed = build_digest_embed(db)
        if not embed:
            print('No high-confidence props to send today')
            return
        async with httpx.AsyncClient() as c:
            r = await c.post(DISCORD_WEBHOOK, json=embed)
            print(f'Discord digest sent: {r.status_code}')
    finally:
        db.close()

async def daily_digest_loop():
    while True:
        now = datetime.utcnow()
        # 11am CST = 17:00 UTC
        if now.hour == 17 and now.minute < 5:
            await send_daily_digest()
            await asyncio.sleep(3600)
        await asyncio.sleep(60)
