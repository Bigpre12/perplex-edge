# External Data Clients

This directory serves as the **Canonical Source of Truth** for all external data provider integrations (TheOddsAPI, SportsDataIO, ESPN, Kalshi, etc.).

## ⚠️ Architectural Guardrails

1. **Backend-Only Invocation**: These clients MUST ONLY be invoked from the FastAPI backend.
2. **Frontend Gating**: The frontend (Web/Mobile) is strictly prohibited from calling external data providers directly. All live odds, statistics, and market data must flow through the backend.
3. **Why?**
   * **Security**: API keys are kept safe in server-side environment variables and never exposed to the client browser.
   * **Resilience**: The `ResilientBaseClient` provides automatic retries, exponential backoff, and circuit breaker logic.
   * **Monetization**: Tier-based feature gating (Pro/Elite) is enforced at the API level via `require_tier` dependencies.
   * **Caching**: Centralized caching in the backend reduces latency and avoids hitting provider rate limits (saving costs).

## Core Clients

* `base_client.py`: Provides `ResilientBaseClient` with logic for retries and circuit breaking.
* `espn_client.py`: Real-time score and injury updates.
* `kalshi_client.py`: Event contract market data.
* `odds_api_client.py`: (In `services/`) Primary provider for live and historical sports odds.

---
*Note: If adding a new provider, inherit from `ResilientBaseClient` to ensure platform consistency.*
