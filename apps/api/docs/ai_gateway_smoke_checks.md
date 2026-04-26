# AI Gateway Smoke Checks

## 1) Baseline (gateway disabled)
- Set `AI_GATEWAY_ENABLED=false`.
- Call chat-backed endpoint(s) that use `ai_service`, `brain_service`, and `oracle_service`.
- Expect unchanged behavior through current provider routes.

## 2) Gateway enabled (valid key)
- Set:
  - `AI_GATEWAY_ENABLED=true`
  - `AI_GATEWAY_API_KEY=<valid>`
  - optional `AI_GATEWAY_MODEL=openai/gpt-5.4`
- Call same endpoints.
- Verify logs show successful gateway transport and responses return normally.

## 3) Gateway enabled (invalid key)
- Keep enabled, set invalid `AI_GATEWAY_API_KEY`.
- Call same endpoints.
- Verify:
  - `ai_service` and `brain_service` log gateway fallback activation,
  - responses still return via direct provider fallback path.

## 4) Oracle gateway transport check
- With gateway enabled, call Oracle streaming endpoint.
- Verify Oracle client initializes against `AI_GATEWAY_BASE_URL` and stream succeeds.
- If gateway auth fails, verify error handling stays graceful.
