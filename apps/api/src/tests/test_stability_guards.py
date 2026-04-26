import os

from core.config import Settings
from core.kalshi_urls import sanitize_kalshi_base_url
from services.stripe_service import StripeService


def test_supabase_role_split_detects_invalid_same_key(monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SUPABASE_KEY", "anon_same")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "anon_same")
    s = Settings()
    assert s.SUPABASE_ROLE_SPLIT_READY is True
    assert s.SUPABASE_SERVICE_KEY_LOOKS_ANON is True


def test_kalshi_url_sanitization_removes_backtick_and_appends_path():
    url = sanitize_kalshi_base_url("https://demo-api.kalshi.co`")
    assert url == "https://demo-api.kalshi.co/trade-api/v2"


def test_stripe_service_rejects_non_price_id():
    svc = StripeService()
    try:
        svc.create_checkout_session(
            price_id="https://buy.stripe.com/abc123",
            customer_email="test@example.com",
            user_id="1",
        )
    except ValueError as exc:
        assert "price_" in str(exc)
    else:
        raise AssertionError("Expected ValueError for non price_ ID")
