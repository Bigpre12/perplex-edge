"""
AI integration layer for Perplex Edge.

Provides a clean, provider-agnostic interface for AI-powered
prop analysis and recommendation generation.

Modules:
    models: Pydantic request/response schemas
    client: HTTP client with retries and structured errors
    service: Orchestration between DB data and AI client
"""

from app.ai.models import (
    AIContext,
    PropLine,
    AIRecommendation,
    AIRecommendationsResponse,
    AIRequestPayload,
)
from app.ai.client import AIClient, AIClientError, AITimeoutError, AIAuthError

__all__ = [
    "AIContext",
    "PropLine",
    "AIRecommendation",
    "AIRecommendationsResponse",
    "AIRequestPayload",
    "AIClient",
    "AIClientError",
    "AITimeoutError",
    "AIAuthError",
]
