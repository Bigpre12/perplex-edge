import asyncio
import os
import sys
import random
from datetime import datetime, timedelta, timezone

# Add src to path
sys.path.append(os.path.join(os.getcwd(), "src"))

from database import async_session_maker
from models.props import PropLine, PropOdds
from models.history import PropHistory
from models.brain import ModelPick

async def generate_mock_data():
    print("🚀 Generating premium mock data for all tabs...")
    async with async_session_maker() as session:
        sports = [
            {"id": 30, "key": "basketball_nba", "players": ["LeBron James", "Kevin Durant", "Stephen Curry", "Nikola Jokic"]},
            {"id": 40, "key": "baseball_mlb", "players": ["Shohei Ohtani", "Aaron Judge", "Mookie Betts"]},
            {"id": 22, "key": "icehockey_nhl", "players": ["Connor McDavid", "Alex Ovechkin"]},
            {"id": 31, "key": "americanfootball_nfl", "players": ["Patrick Mahomes", "Travis Kelce"]}
        ]
        
        stat_types = ["points", "rebounds", "assists", "hits", "goals", "passing_yards"]
        sportsbooks = ["DraftKings", "FanDuel", "BetMGM", "Pinnacle", "Caesars"]

        for sport in sports:
            for player in sport["players"]:
                stat = random.choice(stat_types)
                line_val = random.uniform(1.5, 250.5)
                
                # 1. Create PropLine
                prop = PropLine(
                    player_id=f"p_{random.randint(100, 999)}",
                    player_name=player,
                    team="MockTeam",
                    opponent="MockOpp",
                    sport_key=sport["key"],
                    stat_type=stat,
                    line=round(line_val, 1),
                    game_id=f"g_{random.randint(1000, 9999)}",
                    start_time=datetime.now(timezone.utc) + timedelta(hours=random.randint(1, 24)),
                    sharp_money=random.choice([True, False, False]),
                    steam_score=random.uniform(0, 5.0)
                )
                session.add(prop)
                await session.flush()

                # 2. Create Odds & EV (+EV Tab)
                for book in sportsbooks:
                    ev = random.uniform(-2.0, 8.0)
                    odds_over = random.randint(-150, 150)
                    
                    p_odds = PropOdds(
                        prop_line_id=prop.id,
                        sportsbook=book,
                        over_odds=odds_over,
                        under_odds=-odds_over,
                        ev_percent=round(ev, 2),
                        confidence=random.uniform(40, 90)
                    )
                    session.add(p_odds)
                    
                    # 3. Create ModelPick (Props Tab & Parlay)
                    if ev > 3.0:
                        pick = ModelPick(
                            player_name=player,
                            stat_type=f"player_{stat}",
                            line=prop.line,
                            odds=odds_over,
                            ev_percentage=round(ev, 2),
                            confidence=random.uniform(60, 95),
                            model_probability=random.uniform(0.5, 0.7),
                            sport_id=sport["id"],
                            sport_key=sport["key"],
                            sportsbook=book
                        )
                        session.add(pick)

        await session.commit()
        print("✅ Mock data generation complete!")

if __name__ == "__main__":
    asyncio.run(generate_mock_data())
