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
from services.odds_api_client import odds_api_client

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("seed")

# Configuration moved to centralized OddsApiClient

async def run():
    Path("data").mkdir(exist_ok=True)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    total = 0

    # We'll use the centralized client for everything
    async with httpx.AsyncClient(timeout=30.0) as c:
        # Map our internal SPORTS dict to the seeder's needed format
        # Note: In production, we usually trust OddsApiClient to handle these
        target_sports = [
            ("basketball_nba", 30, ["player_points","player_rebounds","player_assists","player_threes","player_points_rebounds_assists"]),
            ("basketball_ncaab", 39, ["player_points","player_rebounds","player_assists"]),
            ("icehockey_nhl", 22, ["player_points","player_shots_on_goal"]),
            ("baseball_mlb", 40, ["batter_hits","pitcher_strikeouts","batter_total_bases"]),
        ]

        for sport_key, sport_id, markets in target_sports:
            log.info(f"\nProcessing {sport_key}...")
            try:
                # 1. Get Events via client
                events = await odds_api_client.get_live_odds(sport_key)
                if not events or (isinstance(events, dict) and "error" in events):
                    log.warning(f"  No events for {sport_key}")
                    continue
                
                log.info(f"  {len(events)} events found")

                db.query(ModelPick).filter(ModelPick.sport_id == sport_id).delete()
                db.commit()

                n = 0
                for event in events[:8]:
                    event_id = event.get("id")
                    home = event.get("home_team","")
                    away = event.get("away_team","")
                    if not event_id: continue

                    # 2. Get Props via client
                    data = await odds_api_client.get_player_props(sport_key, event_id, markets=",".join(markets))
                    if not data: continue
                    
                    log.info(f"  {away} @ {home} | props found")

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
