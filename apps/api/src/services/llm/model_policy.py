import logging
from typing import Any, Dict, List, Tuple

logger = logging.getLogger(__name__)


def _is_reasoning_model(model: str) -> bool:
    m = (model or "").lower()
    return "grok-4.20-reasoning" in m or m in {
        "grok-4.20",
        "grok-4-1-fast",
        "grok-4.20-multi-agent",
    }


def _is_multi_agent_model(model: str) -> bool:
    return (model or "").lower() == "grok-4.20-multi-agent"


def sanitize_llm_payload(model: str, payload: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
    """
    Remove model-incompatible params from payload and return dropped field names.
    """
    cleaned = dict(payload)
    dropped: List[str] = []

    if _is_reasoning_model(model):
        for key in ("presence_penalty", "frequency_penalty", "stop"):
            if key in cleaned:
                cleaned.pop(key, None)
                dropped.append(key)

    if not _is_multi_agent_model(model):
        if "reasoning" in cleaned:
            cleaned.pop("reasoning", None)
            dropped.append("reasoning")
        if "reasoning_effort" in cleaned:
            cleaned.pop("reasoning_effort", None)
            dropped.append("reasoning_effort")
    else:
        # Multi-agent allows reasoning.effort but not reasoning_effort alias.
        if "reasoning_effort" in cleaned:
            cleaned.pop("reasoning_effort", None)
            dropped.append("reasoning_effort")
        reasoning = cleaned.get("reasoning")
        if reasoning is not None and not isinstance(reasoning, dict):
            cleaned.pop("reasoning", None)
            dropped.append("reasoning")

    return cleaned, dropped


def log_sanitizer_drops(service: str, provider: str, model: str, dropped_fields: List[str]) -> None:
    if dropped_fields:
        logger.info(
            "LLM sanitizer dropped fields service=%s provider=%s model=%s dropped=%s",
            service,
            provider,
            model,
            dropped_fields,
        )
