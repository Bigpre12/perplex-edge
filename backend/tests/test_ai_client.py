"""Unit tests for the AI client module."""

import json
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from app.ai.models import (
    AIContext,
    AIRequestPayload,
    AIRecommendationsResponse,
    PropLine,
    RiskProfile,
    ConfidenceLabel,
    SignalSource,
)
from app.ai.client import (
    AIClient,
    AIClientError,
    AITimeoutError,
    AIAuthError,
    _parse_confidence,
)


# =============================================================================
# Fixtures
# =============================================================================

def make_prop(**overrides) -> PropLine:
    defaults = {
        "game_id": 1,
        "player_name": "Nikola Jokic",
        "stat_type": "PTS",
        "line": 24.5,
        "side": "over",
        "model_probability": 0.62,
        "model_ev": 0.08,
        "confidence": 0.7,
    }
    defaults.update(overrides)
    return PropLine(**defaults)


def make_context(**overrides) -> AIContext:
    defaults = {
        "sport": "NBA",
        "league": "basketball_nba",
        "date": "2026-02-05",
        "risk_profile": RiskProfile.MODERATE,
        "min_ev_threshold": 0.03,
    }
    defaults.update(overrides)
    return AIContext(**defaults)


def make_payload(props=None, context=None) -> AIRequestPayload:
    return AIRequestPayload(
        props=props or [make_prop()],
        context=context or make_context(),
    )


def make_ai_response_json(individual=None, parlays=None, warnings=None) -> dict:
    """Build a mock chat-completion style response from the AI provider."""
    content = json.dumps({
        "individual": individual or [
            {
                "player_name": "Nikola Jokic",
                "stat_type": "PTS",
                "line": 24.5,
                "side": "over",
                "edge_pct": 0.08,
                "confidence_label": "high",
                "reasoning": "Strong matchup advantage",
            }
        ],
        "parlays": parlays or [],
        "warnings": warnings or [],
    })
    return {
        "choices": [
            {
                "message": {
                    "content": content,
                }
            }
        ]
    }


# =============================================================================
# _parse_confidence tests
# =============================================================================

class TestParseConfidence:
    def test_high(self):
        assert _parse_confidence("high") == ConfidenceLabel.HIGH
        assert _parse_confidence("HIGH") == ConfidenceLabel.HIGH
        assert _parse_confidence("h") == ConfidenceLabel.HIGH

    def test_low(self):
        assert _parse_confidence("low") == ConfidenceLabel.LOW
        assert _parse_confidence("LOW") == ConfidenceLabel.LOW
        assert _parse_confidence("l") == ConfidenceLabel.LOW

    def test_medium_default(self):
        assert _parse_confidence("medium") == ConfidenceLabel.MEDIUM
        assert _parse_confidence("") == ConfidenceLabel.MEDIUM
        assert _parse_confidence(None) == ConfidenceLabel.MEDIUM
        assert _parse_confidence("unknown") == ConfidenceLabel.MEDIUM


# =============================================================================
# Model tests
# =============================================================================

class TestModels:
    def test_prop_line_minimal(self):
        prop = PropLine(game_id=1, player_name="Test", stat_type="PTS", line=20.5, side="over")
        assert prop.player_name == "Test"
        assert prop.odds is None

    def test_context_defaults(self):
        ctx = AIContext(sport="NBA", league="basketball_nba", date="2026-02-05")
        assert ctx.risk_profile == RiskProfile.MODERATE
        assert ctx.min_ev_threshold == 0.03
        assert ctx.max_legs_in_parlay == 3

    def test_response_defaults(self):
        resp = AIRecommendationsResponse(sport="NBA", league="basketball_nba", date="2026-02-05")
        assert resp.individual == []
        assert resp.parlays == []
        assert resp.warnings == []
        assert resp.total_recommendations == 0


# =============================================================================
# AIClient tests
# =============================================================================

class TestAIClient:
    @patch("app.ai.client.get_settings")
    def test_init_from_settings(self, mock_settings):
        mock_settings.return_value = MagicMock(
            ai_api_base_url="https://test.api.com",
            ai_api_key="test-key",
            ai_model="test-model",
            ai_timeout_seconds=15,
            ai_max_retries=1,
        )
        client = AIClient()
        assert client.base_url == "https://test.api.com"
        assert client.api_key == "test-key"
        assert client.model == "test-model"
        assert client.timeout == 15
        assert client.max_retries == 1

    @patch("app.ai.client.get_settings")
    def test_init_override(self, mock_settings):
        mock_settings.return_value = MagicMock(
            ai_api_base_url="https://default.com",
            ai_api_key="default-key",
            ai_model="default-model",
            ai_timeout_seconds=30,
            ai_max_retries=2,
        )
        client = AIClient(base_url="https://custom.com", api_key="custom-key", model="custom-model")
        assert client.base_url == "https://custom.com"
        assert client.api_key == "custom-key"
        assert client.model == "custom-model"

    @patch("app.ai.client.get_settings")
    def test_build_prompt(self, mock_settings):
        mock_settings.return_value = MagicMock(
            ai_api_base_url="https://test.com",
            ai_api_key="key",
            ai_model="model",
            ai_timeout_seconds=30,
            ai_max_retries=2,
        )
        client = AIClient()
        payload = make_payload()
        prompt = client._build_prompt(payload)
        assert "NBA" in prompt
        assert "Nikola Jokic" in prompt
        assert "moderate" in prompt

    @patch("app.ai.client.get_settings")
    def test_parse_response_valid(self, mock_settings):
        mock_settings.return_value = MagicMock(
            ai_api_base_url="https://test.com",
            ai_api_key="key",
            ai_model="test-model",
            ai_timeout_seconds=30,
            ai_max_retries=2,
        )
        client = AIClient()
        payload = make_payload()
        raw = make_ai_response_json()
        result = client._parse_response(raw, payload)

        assert isinstance(result, AIRecommendationsResponse)
        assert result.sport == "NBA"
        assert len(result.individual) == 1
        assert result.individual[0].player_name == "Nikola Jokic"
        assert result.individual[0].confidence_label == ConfidenceLabel.HIGH
        assert result.individual[0].signal_source == SignalSource.AI_ASSISTED
        assert result.total_recommendations == 1

    @patch("app.ai.client.get_settings")
    def test_parse_response_invalid_json(self, mock_settings):
        mock_settings.return_value = MagicMock(
            ai_api_base_url="https://test.com",
            ai_api_key="key",
            ai_model="test-model",
            ai_timeout_seconds=30,
            ai_max_retries=2,
        )
        client = AIClient()
        payload = make_payload()
        raw = {"choices": [{"message": {"content": "not valid json {{"}}]}
        result = client._parse_response(raw, payload)

        assert len(result.warnings) > 0
        assert "not valid JSON" in result.warnings[0]

    @patch("app.ai.client.get_settings")
    def test_parse_response_unexpected_shape(self, mock_settings):
        mock_settings.return_value = MagicMock(
            ai_api_base_url="https://test.com",
            ai_api_key="key",
            ai_model="test-model",
            ai_timeout_seconds=30,
            ai_max_retries=2,
        )
        client = AIClient()
        payload = make_payload()
        raw = {"error": "something went wrong"}
        result = client._parse_response(raw, payload)

        assert len(result.warnings) > 0
        assert "unexpected response format" in result.warnings[0]

    @patch("app.ai.client.get_settings")
    def test_parse_response_markdown_fences(self, mock_settings):
        mock_settings.return_value = MagicMock(
            ai_api_base_url="https://test.com",
            ai_api_key="key",
            ai_model="test-model",
            ai_timeout_seconds=30,
            ai_max_retries=2,
        )
        client = AIClient()
        payload = make_payload()
        inner = json.dumps({"individual": [], "parlays": [], "warnings": []})
        raw = {"choices": [{"message": {"content": f"```json\n{inner}\n```"}}]}
        result = client._parse_response(raw, payload)

        assert result.warnings == []
        assert result.individual == []

    @patch("app.ai.client.get_settings")
    @pytest.mark.asyncio
    async def test_analyze_props_no_api_key(self, mock_settings):
        mock_settings.return_value = MagicMock(
            ai_api_base_url="https://test.com",
            ai_api_key="",
            ai_model="model",
            ai_timeout_seconds=30,
            ai_max_retries=2,
        )
        client = AIClient()
        with pytest.raises(AIAuthError):
            await client.analyze_props(make_payload())

    @patch("app.ai.client.get_settings")
    def test_build_request_body(self, mock_settings):
        mock_settings.return_value = MagicMock(
            ai_api_base_url="https://test.com",
            ai_api_key="key",
            ai_model="test-model",
            ai_timeout_seconds=30,
            ai_max_retries=2,
        )
        client = AIClient()
        body = client._build_request_body("test prompt")
        assert body["model"] == "test-model"
        assert len(body["messages"]) == 2
        assert body["messages"][1]["content"] == "test prompt"
        assert body["temperature"] == 0.1


# =============================================================================
# Payload construction tests
# =============================================================================

class TestPayloadConstruction:
    def test_payload_with_multiple_props(self):
        props = [
            make_prop(player_name="Jokic", stat_type="PTS"),
            make_prop(player_name="Murray", stat_type="AST", line=8.5),
        ]
        payload = make_payload(props=props)
        assert len(payload.props) == 2
        assert payload.props[0].player_name == "Jokic"
        assert payload.props[1].line == 8.5

    def test_context_with_injuries(self):
        ctx = make_context(injuries=["LeBron James - Ankle", "AD - Knee"])
        assert len(ctx.injuries) == 2

    def test_context_with_books(self):
        ctx = make_context(books=["FanDuel", "DraftKings"])
        assert ctx.books == ["FanDuel", "DraftKings"]

    @patch("app.ai.client.get_settings")
    def test_prompt_includes_injuries(self, mock_settings):
        mock_settings.return_value = MagicMock(
            ai_api_base_url="https://test.com",
            ai_api_key="key",
            ai_model="model",
            ai_timeout_seconds=30,
            ai_max_retries=2,
        )
        client = AIClient()
        ctx = make_context(injuries=["LeBron James - Ankle"])
        payload = make_payload(context=ctx)
        prompt = client._build_prompt(payload)
        assert "LeBron James" in prompt
        assert "Injuries" in prompt
