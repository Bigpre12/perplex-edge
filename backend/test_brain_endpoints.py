import asyncio
import httpx
import json
import logging
from pprint import pprint

# Set up logging to console
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8001"

async def test_brain_endpoints():
    logger.info("Starting AI Brain Endpoints Test...")

    async with httpx.AsyncClient(timeout=60.0) as client:
        
        # 1. Test /immediate/brain-decisions
        logger.info("\n--- Testing GET /immediate/brain-decisions ---")
        try:
            response = await client.get(f"{BASE_URL}/immediate/brain-decisions?limit=1")
            response.raise_for_status()
            data = response.json()
            logger.info("Status: OK")
            
            decisions = data.get("decisions", [])
            if decisions:
                decision = decisions[0]
                logger.info(f"Generated Decision for: {decision['details']['player_name']}")
                logger.info(f"AI Reasoning:\n{decision['reasoning']}")
                logger.info(f"Duration: {decision['duration_ms']}ms")
            else:
                logger.warning("No decisions returned. Make sure live props are available.")
                
        except Exception as e:
            logger.error(f"Failed /immediate/brain-decisions: {e}")

        # 2. Test /immediate/brain-healing/run-cycle
        logger.info("\n--- Testing POST /immediate/brain-healing/run-cycle ---")
        try:
            response = await client.post(f"{BASE_URL}/immediate/brain-healing/run-cycle")
            response.raise_for_status()
            data = response.json()
            logger.info("Status: OK")
            
            ai_eval = data.get("ai_evaluation", {})
            logger.info(f"AI Selected Action: {ai_eval.get('action')}")
            logger.info(f"AI Target: {ai_eval.get('target')}")
            logger.info(f"AI Reason:\n{ai_eval.get('reason')}")
            logger.info(f"Duration: {data.get('duration_ms')}ms")
                
        except Exception as e:
            logger.error(f"Failed /immediate/brain-healing/run-cycle: {e}")
            
        # 3. Test /parlays/working-parlays (to see the AI reasoning attached)
        logger.info("\n--- Testing GET /parlays/working-parlays ---")
        try:
            response = await client.get(f"{BASE_URL}/parlays/working-parlays?sport=basketball_nba&legs=2")
            response.raise_for_status()
            data = response.json()
            logger.info("Status: OK")
            
            parlays = data.get("parlays", [])
            if parlays:
                parlay = parlays[0]
                logger.info(f"Generated Parlay for Game: {parlay['game_name']}")
                logger.info(f"AI Reasoning Attached:\n{parlay.get('ai_reasoning', 'No reasoning attached')}")
            else:
                logger.warning("No parlays returned.")
                
        except Exception as e:
            logger.error(f"Failed /parlays/working-parlays: {e}")

if __name__ == "__main__":
    asyncio.run(test_brain_endpoints())
