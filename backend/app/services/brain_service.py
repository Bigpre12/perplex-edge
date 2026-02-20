import os
import json
import httpx
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class BrainService:
    def __init__(self):
        self.api_key = os.getenv("AI_API_KEY")
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "llama-3.3-70b-versatile"
        
    async def _call_llm(self, system_prompt: str, user_prompt: str) -> str:
        """Helper to call Groq API with robust error handling"""
        if not self.api_key:
            return "AI API Key not configured. Using fallback reasoning."
            
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 1024
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, json=payload, timeout=30.0)
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
        except Exception as e:
            return f"Error calling Groq API: {str(e)}"

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
        
        # Structure as a "decision" object
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "category": "player_recommendation",
            "action": f"recommend_{player_name.replace(' ', '_').lower()}_{stat_type.lower()}_{side}",
            "reasoning": reasoning.strip(),
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
        
        try:
            # Strip markdown formatting if the model wrapped it in ```json
            clean_text = response_text.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_text)
        except Exception as e:
            logger.error(f"Failed to parse healing response: {response_text}")
            return {
                "action": "none",
                "target": "system",
                "reason": f"Failed to parse AI response: {str(e)}",
                "is_critical": False
            }

brain_service = BrainService()
