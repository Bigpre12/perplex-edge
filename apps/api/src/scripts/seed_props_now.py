import asyncio, os, sys, logging, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from dotenv import load_dotenv; load_dotenv()
import httpx
from datetime import datetime, timezone

Path("data").mkdir(exist_ok=True)
from db.session import engine, Base, SessionLocal
import models.users, models.props, models.brain
from models.brain import ModelPick

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("seed")

KEY = os.getenv("THE_ODDS_API_KEY")
if not KEY:
    log.error("THE_ODDS_API_KEY environment variable is required. Set it in .env or your shell.")
    sys.exit(1)
BASE = "https://api.the-odds-api.com/v4"

SPORTS = {
    "basketball_nba": (30, ["player_points","player_rebounds","player_assists","player_threes","player_points_rebounds_assists"]),
    "basketball_ncaab": (39, ["player_points","player_rebounds","player_assists"]),
    "icehockey_nhl": (22, ["player_points","player_shots_on_goal"]),
    "baseball_mlb": (40, ["batter_hits","pitcher_strikeouts","batter_total_bases"]),
    "mma_mixed_martial_arts": (54, ["h2h"]),
    "tennis_atp_indian_wells": (42, ["h2h"]),
    "tennis_wta_indian_wells": (43, ["h2h"]),
}

def to_prob(odds):
    return (100/(odds+100)) if odds>0 else (abs(odds)/(abs(odds)+100))

def calc_ev(prob, odds):
    return (prob*(odds/100)-(1-prob)) if odds>0 else (prob*(100/abs(odds))-(1-prob))

async def run():
    Path("data").mkdir(exist_ok=True)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    total = 0

    async with httpx.AsyncClient(timeout=30.0) as c:
        # Get active sports
        r = await c.get(f"{BASE}/sports", params={"apiKey": KEY, "all": "false"})
        active = {s["key"] for s in r.json() if s.get("active")} if r.status_code == 200 else set()
        log.info(f"Active sports: {len(active)}")

        for sport_key, (sport_id, markets) in SPORTS.items():
            if sport_key not in active:
                log.info(f"Skipping {sport_key} - not active")
                continue

            log.info(f"\nProcessing {sport_key}...")
            try:
                # Get events
                r_ev = await c.get(f"{BASE}/sports/{sport_key}/events", params={"apiKey": KEY})
                if r_ev.status_code != 200:
                    log.warning(f"  Events failed: {r_ev.status_code}"); continue
                events = r_ev.json()
                log.info(f"  {len(events)} events found")
                if not events:
                    continue

                db.query(ModelPick).filter(ModelPick.sport_id == sport_id).delete()
                db.commit()

                n = 0
                for event in events[:8]:
                    event_id = event.get("id")
                    home = event.get("home_team","")
                    away = event.get("away_team","")
                    if not event_id:
                        continue

                    await asyncio.sleep(0.6)  # Respect rate limit

                    r_odds = await c.get(
                        f"{BASE}/sports/{sport_key}/events/{event_id}/odds",
                        params={
                            "apiKey": KEY,
                            "regions": "us",
                            "markets": ",".join(markets),
                            "oddsFormat": "american",
                            "bookmakers": "draftkings,fanduel,betmgm,caesars,betrivers",
                        }
                    )
                    rem = r_odds.headers.get("x-requests-remaining","?")

                    if r_odds.status_code == 429:
                        log.warning(f"  Rate limited, waiting 5s...")
                        await asyncio.sleep(5)
                        continue
                    if r_odds.status_code != 200:
                        log.warning(f"  {away} @ {home}: {r_odds.status_code}")
                        continue

                    data = r_odds.json()
                    log.info(f"  {away} @ {home} | remaining={rem}")

                    for bm in data.get("bookmakers", []):
                        bm_title = bm.get("title","")
                        bm_key = bm.get("key","")
                        for mkt in bm.get("markets", []):
                            mkt_key = mkt.get("key","")
                            for out in mkt.get("outcomes", []):
                                out_name = out.get("name","")
                                pname = out.get("description","") or out_name
                                line = out.get("point", None)
                                price = out.get("price", -110)

                                # For player props: only overs with a line
                                if line is not None:
                                    if "Over" not in out_name:
                                        continue
                                    side = "over"
                                else:
                                    # Moneyline (h2h) - fighter/player win
                                    side = "moneyline"
                                    line = 0.0
                                    pname = out_name  # fighter name

                                if not pname:
                                    continue

                                import random
                                implied = to_prob(price)
                                
                                # Brain Model Simulation:
                                # We simulate a model that finds "Edges" by comparing the price
                                # to a consensus-derived "Fair Price". 
                                # For this seeder, we'll randomize a fair probability around the implied
                                # but skewed towards finding value on some picks.
                                
                                # 15% of picks are "High Value" (70%+ Confidence)
                                # 35% are "Medium Value" (55-60% Confidence)
                                # 50% are "Low Value/No Edge"
                                rand_val = random.random()
                                if rand_val > 0.85:
                                    model_prob = implied + 0.08 # Significant Edge
                                elif rand_val > 0.50:
                                    model_prob = implied + 0.03 # Small Edge
                                else:
                                    model_prob = implied - 0.02 # No Edge
                                
                                model_prob = max(0.01, min(0.99, model_prob))
                                ev = calc_ev(model_prob, price) * 100
                                
                                # Only seed if it's a "Recommendable" pick for the UI demo
                                if ev < -2:
                                    continue

                                db.add(ModelPick(
                                    player_name=pname,
                                    stat_type=mkt_key,
                                    line=float(line),
                                    side=side,
                                    odds=int(price),
                                    sportsbook=bm_title,
                                    sport_id=sport_id,
                                    sport_key=sport_key,
                                    ev_percentage=ev / 100,
                                    confidence=model_prob * 100,
                                    model_probability=model_prob,
                                    implied_probability=implied,
                                    sharp_money_indicator=(ev > 5.0),
                                    team=home,
                                    status="pending",
                                    created_at=datetime.now(timezone.utc),
                                    updated_at=datetime.now(timezone.utc),
                                ))
                                n += 1

                db.commit()
                total += n
                log.info(f"  Inserted {n} picks for {sport_key}")

            except Exception as e:
                log.error(f"FAILED {sport_key}: {e}")
                import traceback; traceback.print_exc()
                db.rollback()

        count = db.query(ModelPick).count()
        log.info(f"\n{'='*50}")
        log.info(f"DONE. Total inserted: {total} | DB total: {count}")
        if count > 0:
            samples = db.query(ModelPick).limit(5).all()
            for s in samples:
                log.info(f"  {s.player_name} | {s.stat_type} {s.line} {s.side} | {s.odds} | {s.sportsbook} | {s.sport_key}")
    db.close()

asyncio.run(run())
