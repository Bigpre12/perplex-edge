import logging
from typing import Any, Dict, List, Optional, Tuple

import httpx

from core.config import settings
from services.llm.model_policy import sanitize_llm_payload, log_sanitizer_drops

logger = logging.getLogger(__name__)


class AiGatewayError(Exception):
    pass


def is_enabled() -> bool:
    return bool(settings.AI_GATEWAY_ENABLED and settings.AI_GATEWAY_API_KEY)


def _headers() -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {settings.AI_GATEWAY_API_KEY}",
        "Content-Type": "application/json",
    }


def _resolved_model(model: str) -> str:
    return settings.AI_GATEWAY_MODEL or model


async def chat_completion(
    *,
    service_name: str,
    model: str,
    payload: Dict[str, Any],
    timeout_s: float = 30.0,
) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    Returns (response_json, error_message). Never raises for expected transport errors.
    """
    if not is_enabled():
        return None, "gateway_disabled"

    chosen_model = _resolved_model(model)
    data = dict(payload)
    data["model"] = chosen_model
    data, dropped = sanitize_llm_payload(chosen_model, data)
    log_sanitizer_drops(service_name, "ai_gateway", chosen_model, dropped)
    url = f"{settings.AI_GATEWAY_BASE_URL}/chat/completions"

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, headers=_headers(), json=data, timeout=timeout_s)
        if resp.status_code >= 400:
            msg = f"gateway_http_{resp.status_code}"
            logger.warning("AI gateway request failed service=%s error=%s", service_name, msg)
            return None, msg
        logger.info("AI gateway request succeeded service=%s model=%s", service_name, chosen_model)
        return resp.json(), None
    except Exception as exc:
        logger.warning("AI gateway transport failure service=%s error=%s", service_name, exc)
        return None, f"gateway_transport_error:{exc}"
