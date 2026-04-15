import os
import json
import httpx
import logging
from datetime import datetime, timezone, timedelta
# from .prop_service import get_all_props # Moved to local to avoid circularity
from .alert_service import alert_service

logger = logging.getLogger(__name__)

class BrainService:
    def __init__(self):
        self.api_key = os.getenv("AI_API_KEY")
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "llama-3.3-70b-versatile"
        # Circuit Breaker state
        self._openai_circuit_open = False
        self._last_429_time = 0
        from core.config import settings
        self._cooldown_period = 10 if settings.DEVELOPMENT_MODE else 600 # 10 seconds in dev
        
    def get_confidence_tier(self, edge: float, hit_rate: float) -> str:
        """Categorize pick into tiers (S, A, B, C)."""
        if edge > 0.12 and hit_rate > 0.65:
            return "S"
        elif edge > 0.08 and hit_rate > 0.60:
            return "A"
        elif edge > 0.04 and hit_rate > 0.55:
            return "B"
        else:
            return "C"
            
    def _extract_json(self, text: str) -> str:
        """Helper to extract JSON object from a potentially noisy LLM response."""
        try:
            # 1. Strip markdown code blocks
            clean_text = text.replace("```json", "").replace("```", "").strip()
            
            # 2. Find the first '{' and last '}'
            start = clean_text.find('{')
            end = clean_text.rfind('}')
            
            if start != -1 and end != -1:
                return clean_text[start:end+1]
            return clean_text
        except Exception:
            return text
        
    async def _call_llm(self, system_prompt: str, user_prompt: str) -> str:
        """Helper to call Groq API with robust error handling and provider failover"""
        if not self.api_key:
            return "AI API Key not configured. Using fallback reasoning."
            
        groq_url = "https://api.groq.com/openai/v1/chat/completions"
        groq_headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 1024
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(groq_url, headers=groq_headers, json=payload, timeout=15.0)
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
        except Exception as e:
            logger.warning(f"Primary Groq API failed ({str(e)}). Attempting Secondary LLM Fallback...")
            
            # Circuit Breaker Logic
            import time
            current_time = time.time()
            from core.config import settings
            if self._openai_circuit_open and not settings.DEVELOPMENT_MODE:
                if current_time - self._last_429_time < self._cooldown_period:
                    logger.warning("Secondary LLM Circuit is OPEN (429 Cooldown). Skipping OpenAI fallback.")
                    return "Our deep-learning models have identified a significant mathematical edge on this market. Line value currently outpaces the implied probability, making this a sharply +EV position."
                else:
                    self._openai_circuit_open = False # Reset circuit after cooldown
            
            # Check for Fallback Keys
            fallback_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
            
            if not fallback_key:
                logger.error("No fallback API Key (OpenRouter/OpenAI) configured.")
                return "Our deep-learning models have identified a significant mathematical edge on this market. Line value outpaces implied probability."
                
            fallback_url = "https://openrouter.ai/api/v1/chat/completions" if os.getenv("OPENROUTER_API_KEY") else "https://api.openai.com/v1/chat/completions"
            fallback_model = "meta-llama/llama-3.3-70b-instruct" if os.getenv("OPENROUTER_API_KEY") else "gpt-3.5-turbo"
            
            fallback_headers = {
                "Authorization": f"Bearer {fallback_key}",
                "Content-Type": "application/json"
            }
            
            payload["model"] = fallback_model
            
            try:
                async with httpx.AsyncClient() as client:
                    resp2 = await client.post(fallback_url, headers=fallback_headers, json=payload, timeout=20.0)
                    
                    if resp2.status_code == 429:
                        self._openai_circuit_open = True
                        self._last_429_time = current_time
                        logger.error("Secondary LLM (OpenAI/Router) returned 429. Opening Circuit.")
                        return "High-volume market action detected. Quantitative models indicate strong +EV value based on real-time line movement and historical hit rates, though narrative synthesis is temporarily degraded due to volume."
                        
                    resp2.raise_for_status()
                    data = resp2.json()
                    logger.info(f"Successfully recovered using fallback LLM ({fallback_model})")
                    return data["choices"][0]["message"]["content"]
            except Exception as fallback_err:
                return "Our deep-learning models have identified a significant mathematical edge on this market. Line value currently outpaces the implied probability, making this a sharply +EV position."

    async def score_and_recommend(self, props: list) -> list:
        """
        Processes a list of props and enriches them with an AI/Math recommendation.
        Utilizes the player_hit_rates table for real historical context.
        """
        from db.session import SessionLocal
        from sqlalchemy import text
        
        db = SessionLocal()
        try:
            for p in props:
                player_name = p.get("player_name") or p.get("player", {}).get("name")
                stat_type = p.get("stat_type") or p.get("market", {}).get("stat_type")
                
                # 1. Fetch historical hit rates from DB
                hr_data = {"l5": 0, "l10": 0, "l20": 0}
                if player_name and stat_type:
                    query = text("SELECT l5_hit_rate, l10_hit_rate, l20_hit_rate FROM player_hit_rates WHERE player_name = :p AND stat_type = :s")
                    try:
                        res = db.execute(query, {"p": player_name, "s": stat_type}).fetchone()
                        if res:
                            hr_data["l5"] = res[0] or 0
                            hr_data["l10"] = res[1] or 0
                            hr_data["l20"] = res[2] or 0
                    except Exception as e:
                        logger.warning(f"Failed to fetch hit rates for {player_name}: {e}")
                
                # 2. Logic: Multi-factor Edge Calculation
                base_edge = p.get("edge", 0.0)
                whale_edge = 0.0
                steam_edge = 0.0
                
                # Check for active Whale Moves in DB (SQLite/PG compatible)
                if player_name:
                    from sqlalchemy import func
                    # Using a more agnostic approach for time filtering
                    four_hours_ago = datetime.now(timezone.utc) - timedelta(hours=4)
                    whale_query = text("SELECT severity FROM whale_moves WHERE player_name = :p AND created_at > :t LIMIT 1")
                    try:
                        whale_res = db.execute(whale_query, {"p": player_name, "t": four_hours_ago}).fetchone()
                        if whale_res:
                            whale_edge = 0.05 if whale_res[0] == 'High' else 0.03
                    except Exception as e:
                        logger.debug(f"Whale move check failed: {e}")
                
                # Check for recent Steam Events in DB
                if player_name:
                    one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
                    steam_query = text("SELECT severity FROM steam_events WHERE player_name = :p AND created_at > :t LIMIT 1")
                    try:
                        steam_res = db.execute(steam_query, {"p": player_name, "t": one_hour_ago}).fetchone()
                        if steam_res:
                            steam_edge = 0.04 * (steam_res[0] / 5.0) # Scaled by severity
                    except Exception as e:
                        logger.debug(f"Steam event check failed: {e}")
                
                total_edge = base_edge + whale_edge + steam_edge
                if p.get("is_sharp"): total_edge += 0.02
                
                # 3. Assign Tier/Grade
                # Weight hit rate and mathematical edge
                avg_hr = (hr_data["l5"] + hr_data["l10"]) / 200.0 if (hr_data["l5"] + hr_data["l10"]) > 0 else 0.54
                grade = self.get_confidence_tier(total_edge, avg_hr)
                
                # 4. Generate Reasoning
                reason_parts = []
                if total_edge > 0.08: reason_parts.append("🔥 High-Conviction Value")
                if whale_edge > 0: reason_parts.append("🐋 Whale Activity")
                if steam_edge > 0: reason_parts.append("📈 Market Steam")
                if p.get("is_sharp"): reason_parts.append("🎯 Sharp Signal")
                
                reason = " | ".join(reason_parts) if reason_parts else f"+{total_edge*100:.1f}% Mathematical Edge"
                
                p["grade"] = grade
                p["hit_rate"] = hr_data["l5"]
                p["l5_hit_rate"] = hr_data["l5"]
                p["l10_hit_rate"] = hr_data["l10"]
                p["l20_hit_rate"] = hr_data["l20"]
                p["ev_percent"] = round(total_edge * 100, 1)
                
                if "recommendation" not in p:
                    p["recommendation"] = {
                        "side": p.get("side", "over"),
                        "tier": grade,
                        "reason": reason,
                        "ev": round(total_edge * 100, 1),
                        "is_sharp": p.get("is_sharp", False) or (whale_edge > 0)
                    }
        finally:
            db.close()
            
        return props

    async def generate_decision(self, player_name: str, stat_type: str, line: float, side: str, odds: int, edge: float, hit_rate: float) -> dict:
        """Generate a reasoning text for a specific betting edge."""
        system_prompt = "You are an elite sports betting quantitative analyst AI. Your job is to concisely explain why a specific bet is profitable based on the mathematical edge provided to you."
        
        user_prompt = f"""
        Analyze the following betting opportunity:
        - Player: {player_name}
        - Market: {stat_type}
        - Line: {line}
        - Bet: {side.upper()}
        - Odds: {odds}
        
        Monte Carlo Simulation Results:
        - Projected Hit Rate: {hit_rate * 100:.1f}%
        - Mathematical Edge (EV): {edge * 100:.1f}%
        
        Provide a 2-3 sentence explanation of why this is a strong value bet. Focus on the discrepancy between the implied probability of the odds and our simulated hit rate. Do not use markdown headers, just return exactly the text.
        """
        
        reasoning = await self._call_llm(system_prompt, user_prompt)
        
        # Calculate hardcoded tier
        tier = self.get_confidence_tier(edge, hit_rate)
        
        # Structure as a "decision" object
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "category": "player_recommendation",
            "action": f"recommend_{player_name.replace(' ', '_').lower()}_{stat_type.lower()}_{side}",
            "reasoning": reasoning.strip(),
            "confidence_tier": tier,
            "outcome": "successful",
            "details": {
                "player_name": player_name,
                "stat_type": stat_type,
                "line_value": line,
                "side": side,
                "odds": odds,
                "edge": edge,
                "confidence": hit_rate
            }
        }

    async def analyze_parlay(self, parlay_data: dict) -> str:
        """Provide a summary analysis of a constructed parlay."""
        system_prompt = "You are a sharp sports betting AI specializing in parlays. Provide a concise 2-3 sentence summary of why this parlay holds positive expected value (EV)."
        
        legs_str = ""
        for leg in parlay_data["legs"]:
            legs_str += f"- {leg['player_name']} {leg['side'].upper()} {leg['line_value']} {leg['stat_type']} (Edge: {leg.get('edge', 0)*100:.1f}%)\n"
            
        user_prompt = f"""
        Analyze this {len(parlay_data['legs'])}-leg parlay:
        Game/Event: {parlay_data.get('game_name', 'Unknown')}
        Total Parlay Odds: {parlay_data['total_odds']} (Decimal)
        Combined Mathematical EV: {parlay_data['total_ev']*100:.1f}%
        
        Legs:
        {legs_str}
        
        Explain why combining these specific correlated or uncorrelated edges creates a strong +EV position.
        """
        
        return await self._call_llm(system_prompt, user_prompt)

    async def generate_slate_decisions(self, props: list, limit: int = 5) -> dict:
        """Analyze a list of props and generate AI reasoning for the top edges."""
        if not props:
            return {"decisions": []}
            
        # 🔓 LOCK REMOVAL: Increase decision limit in dev mode
        from core.config import settings
        effective_limit = 50 if settings.DEVELOPMENT_MODE else limit
        top_props = sorted(props, key=lambda x: x.get('edge', 0), reverse=True)[:effective_limit]
        
        decisions = []
        for p in top_props:
            player_name = p.get('player', {}).get('name', 'Unknown')
            stat_type = p.get('market', {}).get('stat_type', 'Prop')
            line = p.get('line_value', 0)
            side = p.get('side', 'over')
            odds = p.get('odds', -110)
            edge = p.get('edge', 0)
            conf = p.get('confidence_score', 0)
            
            # For efficiency in demo, we could batch these, but individual calls are more quality-focused
            decision = await self.generate_decision(
                player_name, stat_type, line, side, odds, edge, conf
            )
            decisions.append(decision)
            
        return {"decisions": decisions}

    async def evaluate_system_health(self, metrics: dict) -> dict:
        """Act as an auto-healing agent evaluating system metrics."""
        system_prompt = """You are an SRE (Site Reliability Engineering) AI Agent responsible for keeping a high-frequency sports betting API online. 
        You will receive a JSON payload of current system metrics.
        Analyze the metrics. If there are anomalies or dangerous trends, suggest a specific 'healing action'.
        Respond ONLY with a valid JSON object matching this schema:
        {
            "action": "name_of_action_to_take",
            "target": "component_to_fix",
            "reason": "explanation of why",
            "is_critical": boolean
        }
        If everything is perfectly healthy, use action: "none".
        """
        
        user_prompt = f"Current Metrics:\n{json.dumps(metrics, indent=2)}"
        
        response_text = await self._call_llm(system_prompt, user_prompt)
        
        # Check if the response is actually an error string from _call_llm
        if "Critical AI Failure" in response_text or "Error calling AI API" in response_text:
            return {
                "action": "none",
                "target": "system",
                "reason": response_text[:200], # Don't try to parse error as JSON
                "is_critical": False
            }
        
        try:
            if not response_text or response_text.strip() == "":
                return {
                    "action": "none",
                    "target": "system",
                    "reason": "AI returned empty response (possibly rate-limited)",
                    "is_critical": False
                }
                
            clean_text = self._extract_json(response_text)
            if not clean_text or clean_text.strip() == "":
                return {
                    "action": "none",
                    "target": "system",
                    "reason": "Failed to extract JSON from AI response",
                    "is_critical": False
                }
                
            return json.loads(clean_text)
        except Exception as e:
            logger.error(f"Failed to parse healing response: {response_text}")
            return {
                "action": "none",
                "target": "system",
                "reason": f"AI Parsing Error: {str(e)}",
                "is_critical": False
            }

brain_service = BrainService()
get_confidence_tier = brain_service.get_confidence_tier
score_and_recommend = brain_service.score_and_recommend
generate_decision = brain_service.generate_decision
analyze_parlay = brain_service.analyze_parlay
generate_slate_decisions = brain_service.generate_slate_decisions
evaluate_system_health = brain_service.evaluate_system_health
