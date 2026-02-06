"""
AI client for Perplex Edge.

Provider-agnostic HTTP client that sends structured prop data to an AI
analysis API and returns normalized recommendations. Designed to be
easily swapped between providers (Perplexity, OpenAI, Anthropic, etc.).
"""

import json
import logging
from typing import Optional

import httpx

from app.ai.models import (
    AIRequestPayload,
    AIRecommendation,
    AIRecommendationsResponse,
    ParlayRecommendation,
    ConfidenceLabel,
    SignalSource,
)
from app.core.config import get_settings

logger = logging.getLogger(__name__)


# =============================================================================
# Exceptions
# =============================================================================

class AIClientError(Exception):
    """Base exception for AI client errors."""

    def __init__(self, message: str, status_code: Optional[int] = None):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class AITimeoutError(AIClientError):
    """Raised when the AI API request times out."""
    pass


class AIAuthError(AIClientError):
    """Raised when the AI API returns an authentication error."""
    pass


# =============================================================================
# Default Prompt
# =============================================================================

DEFAULT_PROMPT_TEMPLATE = """You are an expert sports betting analyst for Perplex Edge.

Analyze the following {sport} player props for {date} and return structured JSON recommendations.

RULES:
- Only recommend props with positive expected value (EV > {min_ev_threshold}).
- Rank by edge percentage descending.
- For each recommendation include: player_name, stat_type, line, side, edge_pct, confidence_label (low/medium/high), and brief reasoning.
- If you can form valid parlays (2-{max_legs} uncorrelated legs), include them.
- Return ONLY valid JSON matching the schema below. No markdown, no extra text.

SCHEMA:
{{
  "individual": [
    {{
      "player_name": "string",
      "stat_type": "string",
      "line": number,
      "side": "over|under",
      "edge_pct": number,
      "confidence_label": "low|medium|high",
      "reasoning": "string"
    }}
  ],
  "parlays": [
    {{
      "legs": [{{ "player_name": "string", "stat_type": "string", "line": number, "side": "string", "edge_pct": number, "confidence_label": "string" }}],
      "combined_ev": number,
      "confidence_label": "low|medium|high",
      "reasoning": "string"
    }}
  ],
  "warnings": ["string"]
}}

PROPS DATA:
{props_json}

CONTEXT:
- Risk profile: {risk_profile}
- Min EV threshold: {min_ev_threshold}
{extra_context}
"""


# =============================================================================
# Client
# =============================================================================

class AIClient:
    """
    HTTP client for AI-powered prop analysis.

    Usage:
        client = AIClient()
        response = await client.analyze_props(payload)
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        timeout: Optional[int] = None,
        max_retries: Optional[int] = None,
    ):
        settings = get_settings()
        self.base_url = (base_url or settings.ai_api_base_url).rstrip("/")
        self.api_key = api_key or settings.ai_api_key
        self.model = model or settings.ai_model
        self.timeout = timeout or settings.ai_timeout_seconds
        self.max_retries = max_retries if max_retries is not None else settings.ai_max_retries

    def _build_prompt(self, payload: AIRequestPayload) -> str:
        """Build the prompt string from the payload and template."""
        template = payload.prompt_template or DEFAULT_PROMPT_TEMPLATE

        props_json = json.dumps(
            [p.model_dump(exclude_none=True) for p in payload.props],
            indent=2,
        )

        extra_lines = []
        if payload.context.injuries:
            extra_lines.append(f"- Injuries: {', '.join(payload.context.injuries)}")
        if payload.context.books:
            extra_lines.append(f"- Preferred books: {', '.join(payload.context.books)}")
        if payload.context.notes:
            extra_lines.append(f"- Notes: {payload.context.notes}")

        return template.format(
            sport=payload.context.sport,
            date=payload.context.date,
            min_ev_threshold=payload.context.min_ev_threshold,
            max_legs=payload.context.max_legs_in_parlay,
            risk_profile=payload.context.risk_profile.value,
            props_json=props_json,
            extra_context="\n".join(extra_lines) if extra_lines else "None",
        )

    def _build_request_body(self, prompt: str) -> dict:
        """Build the HTTP request body for the AI provider."""
        return {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a sports betting analytics engine. Return only valid JSON.",
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            "temperature": 0.1,
            "max_tokens": 4096,
        }

    def _parse_response(
        self, raw: dict, payload: AIRequestPayload
    ) -> AIRecommendationsResponse:
        """Parse the raw AI API response into our normalized schema."""
        warnings: list[str] = []

        # Extract content from chat-completion style response
        try:
            content = raw["choices"][0]["message"]["content"]
        except (KeyError, IndexError):
            logger.warning("ai_response_unexpected_shape", raw_keys=list(raw.keys()))
            return AIRecommendationsResponse(
                sport=payload.context.sport,
                league=payload.context.league,
                date=payload.context.date,
                warnings=["AI returned an unexpected response format"],
                ai_model=self.model,
            )

        # Strip markdown fences if present
        content = content.strip()
        if content.startswith("```"):
            content = content.split("\n", 1)[-1]
        if content.endswith("```"):
            content = content.rsplit("```", 1)[0]
        content = content.strip()

        # Parse JSON
        try:
            data = json.loads(content)
        except json.JSONDecodeError as e:
            logger.warning("ai_response_json_parse_error", error=str(e)[:200])
            return AIRecommendationsResponse(
                sport=payload.context.sport,
                league=payload.context.league,
                date=payload.context.date,
                warnings=[f"AI response was not valid JSON: {str(e)[:100]}"],
                ai_model=self.model,
            )

        # Map individual recommendations
        individual: list[AIRecommendation] = []
        for rec in data.get("individual", []):
            try:
                individual.append(AIRecommendation(
                    player_name=rec["player_name"],
                    stat_type=rec.get("stat_type", ""),
                    line=float(rec.get("line", 0)),
                    side=rec.get("side", "over"),
                    edge_pct=rec.get("edge_pct"),
                    confidence_label=_parse_confidence(rec.get("confidence_label")),
                    reasoning=rec.get("reasoning"),
                    signal_source=SignalSource.AI_ASSISTED,
                ))
            except (KeyError, ValueError) as e:
                warnings.append(f"Skipped malformed recommendation: {str(e)[:80]}")

        # Map parlay recommendations
        parlays: list[ParlayRecommendation] = []
        for par in data.get("parlays", []):
            try:
                parlays.append(ParlayRecommendation(
                    legs=[
                        {
                            "player_name": leg["player_name"],
                            "stat_type": leg.get("stat_type", ""),
                            "line": float(leg.get("line", 0)),
                            "side": leg.get("side", "over"),
                            "edge_pct": leg.get("edge_pct"),
                            "confidence_label": _parse_confidence(leg.get("confidence_label")),
                        }
                        for leg in par.get("legs", [])
                    ],
                    combined_ev=par.get("combined_ev"),
                    confidence_label=_parse_confidence(par.get("confidence_label")),
                    reasoning=par.get("reasoning"),
                ))
            except (KeyError, ValueError) as e:
                warnings.append(f"Skipped malformed parlay: {str(e)[:80]}")

        # Merge warnings from AI response
        warnings.extend(data.get("warnings", []))

        return AIRecommendationsResponse(
            sport=payload.context.sport,
            league=payload.context.league,
            date=payload.context.date,
            individual=individual,
            parlays=parlays,
            warnings=warnings,
            total_recommendations=len(individual) + len(parlays),
            ai_model=self.model,
        )

    async def analyze_props(
        self, payload: AIRequestPayload
    ) -> AIRecommendationsResponse:
        """
        Send props to the AI provider and return normalized recommendations.

        Args:
            payload: Structured request with props and context.

        Returns:
            AIRecommendationsResponse with individual and parlay recommendations.

        Raises:
            AIAuthError: If the API key is invalid.
            AITimeoutError: If the request times out.
            AIClientError: For other HTTP errors.
        """
        if not self.api_key:
            raise AIAuthError("AI_API_KEY is not configured")

        prompt = self._build_prompt(payload)
        body = self._build_request_body(prompt)

        logger.info(
            "ai_request_start",
            model=self.model,
            props_count=len(payload.props),
            sport=payload.context.sport,
        )

        last_error: Optional[Exception] = None
        for attempt in range(1, self.max_retries + 2):  # +2 because range is exclusive and attempt 1 is the initial try
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(
                        f"{self.base_url}/chat/completions",
                        json=body,
                        headers={
                            "Authorization": f"Bearer {self.api_key}",
                            "Content-Type": "application/json",
                        },
                    )

                if response.status_code == 401:
                    raise AIAuthError("Invalid AI API key", status_code=401)
                if response.status_code == 429:
                    logger.warning("ai_rate_limited", attempt=attempt)
                    last_error = AIClientError("Rate limited", status_code=429)
                    continue
                if response.status_code >= 500:
                    logger.warning("ai_server_error", status=response.status_code, attempt=attempt)
                    last_error = AIClientError(f"AI server error: {response.status_code}", status_code=response.status_code)
                    continue

                response.raise_for_status()
                raw = response.json()

                result = self._parse_response(raw, payload)
                logger.info(
                    "ai_request_complete",
                    recommendations=result.total_recommendations,
                    warnings=len(result.warnings),
                )
                return result

            except httpx.TimeoutException:
                logger.warning("ai_request_timeout", attempt=attempt, timeout=self.timeout)
                last_error = AITimeoutError(f"AI request timed out after {self.timeout}s")
            except (AIAuthError, AIClientError):
                raise
            except httpx.HTTPStatusError as e:
                last_error = AIClientError(f"HTTP error: {e.response.status_code}", status_code=e.response.status_code)
                logger.warning("ai_http_error", status=e.response.status_code, attempt=attempt)
            except Exception as e:
                last_error = AIClientError(f"Unexpected error: {str(e)[:200]}")
                logger.error("ai_unexpected_error", error=str(e)[:200], attempt=attempt)

        # All retries exhausted
        if last_error:
            raise last_error
        raise AIClientError("AI request failed after all retries")


# =============================================================================
# Helpers
# =============================================================================

def _parse_confidence(value: Optional[str]) -> ConfidenceLabel:
    """Safely parse a confidence label string."""
    if not value:
        return ConfidenceLabel.MEDIUM
    value = value.lower().strip()
    if value in ("high", "h"):
        return ConfidenceLabel.HIGH
    if value in ("low", "l"):
        return ConfidenceLabel.LOW
    return ConfidenceLabel.MEDIUM
