from services.llm.model_policy import sanitize_llm_payload


def test_reasoning_model_strips_penalties_and_stop():
    payload = {
        "model": "grok-4.20-reasoning",
        "messages": [{"role": "user", "content": "hi"}],
        "presence_penalty": 0.3,
        "frequency_penalty": 0.2,
        "stop": ["END"],
    }
    cleaned, dropped = sanitize_llm_payload("grok-4.20-reasoning", payload)
    assert "presence_penalty" not in cleaned
    assert "frequency_penalty" not in cleaned
    assert "stop" not in cleaned
    assert set(["presence_penalty", "frequency_penalty", "stop"]).issubset(set(dropped))


def test_grok_non_multi_agent_strips_reasoning_fields():
    payload = {
        "model": "grok-4.20",
        "messages": [{"role": "user", "content": "hi"}],
        "reasoning": {"effort": "high"},
        "reasoning_effort": "high",
    }
    cleaned, dropped = sanitize_llm_payload("grok-4.20", payload)
    assert "reasoning" not in cleaned
    assert "reasoning_effort" not in cleaned
    assert "reasoning" in dropped
    assert "reasoning_effort" in dropped


def test_multi_agent_keeps_reasoning_effort_object():
    payload = {
        "model": "grok-4.20-multi-agent",
        "messages": [{"role": "user", "content": "hi"}],
        "reasoning": {"effort": "high"},
        "reasoning_effort": "high",
    }
    cleaned, dropped = sanitize_llm_payload("grok-4.20-multi-agent", payload)
    assert cleaned.get("reasoning") == {"effort": "high"}
    assert "reasoning_effort" not in cleaned
    assert "reasoning_effort" in dropped
