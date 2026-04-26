import importlib
import pytest


def _reload_helper():
    config_mod = importlib.import_module("core.config")
    importlib.reload(config_mod)
    helper_mod = importlib.import_module("services.llm.ai_gateway_client")
    importlib.reload(helper_mod)
    return helper_mod


def test_ai_gateway_config_defaults_and_overrides(monkeypatch):
    monkeypatch.setenv("AI_GATEWAY_ENABLED", "true")
    monkeypatch.setenv("AI_GATEWAY_API_KEY", "gw_test_key")
    monkeypatch.setenv("AI_GATEWAY_BASE_URL", "https://ai-gateway.vercel.sh/v1")
    monkeypatch.setenv("AI_GATEWAY_MODEL", "openai/gpt-5.4")

    config = importlib.import_module("core.config")
    s = config.Settings()
    assert s.AI_GATEWAY_ENABLED is True
    assert s.AI_GATEWAY_API_KEY == "gw_test_key"
    assert s.AI_GATEWAY_BASE_URL == "https://ai-gateway.vercel.sh/v1"
    assert s.AI_GATEWAY_MODEL == "openai/gpt-5.4"


@pytest.mark.asyncio
async def test_ai_gateway_helper_disabled(monkeypatch):
    monkeypatch.setenv("AI_GATEWAY_ENABLED", "false")
    monkeypatch.setenv("AI_GATEWAY_API_KEY", "")

    helper = _reload_helper()
    data, err = await helper.chat_completion(
        service_name="test",
        model="openai/gpt-5.4",
        payload={"messages": [{"role": "user", "content": "hi"}]},
    )
    assert data is None
    assert err == "gateway_disabled"


@pytest.mark.asyncio
async def test_ai_gateway_helper_transport_error(monkeypatch):
    monkeypatch.setenv("AI_GATEWAY_ENABLED", "true")
    monkeypatch.setenv("AI_GATEWAY_API_KEY", "gw_test_key")
    monkeypatch.setenv("AI_GATEWAY_BASE_URL", "https://ai-gateway.vercel.sh/v1")

    helper = _reload_helper()

    class _BoomClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def post(self, *args, **kwargs):
            raise RuntimeError("network down")

    monkeypatch.setattr(helper.httpx, "AsyncClient", lambda *args, **kwargs: _BoomClient())

    data, err = await helper.chat_completion(
        service_name="test",
        model="openai/gpt-5.4",
        payload={"messages": [{"role": "user", "content": "hi"}]},
    )
    assert data is None
    assert "gateway_transport_error" in (err or "")
