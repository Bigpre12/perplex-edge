"""
Working Parlays Router — Backward-compatible parlay & Monte Carlo endpoints.

Now delegates to the real monte_carlo_service instead of returning hardcoded data.
"""
import random
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.monte_carlo_service import monte_carlo_service
from app.real_data_connector import real_data_connector
from app.services.brain_service import brain_service

router = APIRouter()


@router.get("/working-parlays")
async def get_working_parlays(
    sport_key: str = Query("basketball_nba", description="The Odds API sport key"),
    game_id: str = Query(None, description="External Game ID (leave empty to pick a random live game)"),
    limit: int = Query(5, description="Number of parlays to generate"),
    db=Depends(get_db),
):
    """Generate realistic sample parlays using live Odds API data and Monte Carlo edges."""
    try:
        # 1. Fetch live games and pick one if game_id is not provided
        games = await real_data_connector.fetch_nba_games() if "nba" in sport_key else await real_data_connector.fetch_nfl_games()
        
        if not games:
            raise HTTPException(status_code=404, detail="No live games found for parlay generation")
            
        target_game_id = game_id or games[0].get("id")
        
        # 2. Fetch live player props for this game (Points market used as default)
        props = await real_data_connector.fetch_player_props(sport_key, target_game_id, "player_points")
        
        if len(props) < 3:
            raise HTTPException(status_code=404, detail=f"Not enough player props found for game {target_game_id}")
            
        # Extract unique players to build parlay combinations
        unique_players = list({p["player_name"]: p for p in props}.values())
        
        # 3. Build sample parlay definitions
        result_parlays = []
        parlay_id = 1
        
        for _ in range(limit):
            # Pick 2-4 random legs for the parlay
            num_legs = random.randint(2, min(4, len(unique_players)))
            selected_props = random.sample(unique_players, num_legs)
            
            legs_def = []
            for prop in selected_props:
                # To simulate reality, we assume the true mean is close to the line
                # In a real system, the mean/std_dev would come from your ML projections model
                simulated_mean = prop["line"] * random.uniform(0.85, 1.15) 
                
                legs_def.append({
                    "player_name": prop["player_name"],
                    "stat_type": prop["stat_type"],
                    "mean": simulated_mean,
                    "std_dev": simulated_mean * 0.2, # 20% variance estimator
                    "line": prop["line"],
                    "side": "over" if random.choice([True, False]) else "under",
                    "odds": prop["over_odds"] if random.choice([True, False]) else prop["under_odds"]
                })
                
            # 4. Run real Monte Carlo simulation on this parlay definition
            mc_result = monte_carlo_service.simulate_parlay(
                legs=legs_def, n_sims=5000
            )

            # 5. Format legs for response
            formatted_legs = []
            for i, leg in enumerate(legs_def):
                leg_mc = mc_result["leg_results"][i] if i < len(mc_result["leg_results"]) else {}
                formatted_legs.append({
                    "player_name": leg["player_name"],
                    "stat_type": leg["stat_type"],
                    "line_value": leg["line"],
                    "side": leg["side"],
                    "odds": leg["odds"],
                    "edge": leg_mc.get("edge", 0),
                    "simulated_hit_rate": leg_mc.get("simulated_hit_rate", 0),
                })

            parlay_dict = {
                "id": parlay_id,
                "game_id": target_game_id,
                "game_name": f"{games[0].get('away_team_name')} @ {games[0].get('home_team_name')}",
                "total_ev": mc_result["parlay_ev"],
                "total_odds": mc_result["combined_decimal_odds"],
                "parlay_hit_rate": mc_result["parlay_hit_rate"],
                "legs": formatted_legs,
                "confidence_score": mc_result["parlay_hit_rate"],
                "simulations": mc_result["simulations"],
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
            
            # 6. Generate AI reasoning for this specific parlay configuration
            parlay_dict["ai_reasoning"] = await brain_service.analyze_parlay(parlay_dict)
            
            result_parlays.append(parlay_dict)
            parlay_id += 1

        return {
            "game_name": f"{games[0].get('away_team_name')} @ {games[0].get('home_team_name')}",
            "parlays": result_parlays,
            "total": len(result_parlays),
            "sport_key": sport_key,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "The Odds API + Monte Carlo Engine"
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        return {
            "parlays": [],
            "total": 0,
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


@router.get("/monte-carlo-simulation")
async def get_monte_carlo_simulation(
    sport_key: str = Query("basketball_nba", description="The Odds API sport key"),
    game_id: str = Query(None, description="External Game ID (leave empty to pick a random live game)"),
    simulations: int = Query(5000, description="Number of simulations"),
    db=Depends(get_db),
):
    """
    Monte Carlo simulation endpoint using Live Data.

    Generates player stat distributions against Odds API real lines
    using the monte_carlo_service engine.
    """
    try:
        # 1. Fetch live games and pick one if game_id is not provided
        games = await real_data_connector.fetch_nba_games() if "nba" in sport_key else await real_data_connector.fetch_nfl_games()
        
        if not games:
            raise HTTPException(status_code=404, detail="No live games found for MC simulation")
            
        target_game_id = game_id or games[0].get("id")

        # 2. Fetch live props across multiple markets to analyze
        markets = ["player_points", "player_rebounds", "player_assists"] if "nba" in sport_key else ["player_pass_yds", "player_rush_yds"]
        
        all_props = []
        for market in markets:
            props = await real_data_connector.fetch_player_props(sport_key, target_game_id, market)
            all_props.extend(props[:10]) # Limit to top 10 per market for reasonable API speed
            
        if not all_props:
            raise HTTPException(status_code=404, detail="No player props found for Monte Carlo simulation")
            
        # Run real simulations per prop
        results = {}
        probabilities = {}

        for prop in all_props:
            player_key = prop["player_name"].replace(" ", "_").lower()
            stat_key = prop["stat_type"]
            
            if player_key not in results:
                results[player_key] = {}
                
            # Simulate projections (mock ML means - variance around the line)
            simulated_mean = prop["line"] * random.uniform(0.9, 1.1)
            std_dev = simulated_mean * 0.2
            
            sim_result = monte_carlo_service.simulate_prop(
                mean=simulated_mean,
                std_dev=std_dev,
                line=prop["line"],
                side="over",
                n_sims=simulations,
                distribution="normal" if "points" in stat_key or "yds" in stat_key else "poisson",
            )

            results[player_key][stat_key] = {
                "mean": sim_result["mean"],
                "median": sim_result["median"],
                "std_dev": sim_result["std_dev"],
                "percentiles": sim_result["percentiles"],
                "actual_line": prop["line"],
                "simulated_mean": round(simulated_mean, 1)
            }

            prob_key = f"{player_key}_{stat_key}_over_{prop['line']}"
            probabilities[prob_key] = sim_result["hit_rate"]

        return {
            "game_id": target_game_id,
            "sport_key": sport_key,
            "simulations_run": simulations,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "results": results,
            "probabilities": probabilities,
            "source": "The Odds API + Monte Carlo Engine"
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
