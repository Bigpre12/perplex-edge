# Phase 0 Schema Drift Map

This file identifies schema authority and currently observed drift vectors.

## Authority

- Migration authority: `apps/api/src/alembic/versions/*.py`
- ORM authority: `apps/api/src/models/*.py`
- Drift source to eliminate: startup DDL in `apps/api/src/main.py`

## Observed Drift Risks

1. **Startup DDL owns production schema mutation**
   - `main.py` executes a long chain of `ALTER TABLE`, index rebuilds, and cleanup updates.
   - This bypasses migration history and causes uncertain state across environments.

2. **Model vs runtime column mismatch**
   - Recent runtime failures showed missing `whale_moves` columns (`market_key`, `selection`) despite model/query expectations.
   - Indicates DB schema and ORM assumptions can diverge independently from Alembic.

3. **Constraint/index lifecycle split**
   - Unique constraints and indexes are dropped/re-created in startup code.
   - These should be deterministic migration steps, not process boot side effects.

## Normalization Targets

1. Move stable startup DDL to Alembic migration scripts.
2. Keep only emergency safety checks in startup, behind feature flag.
3. Add schema compatibility checks for high-risk tables:
   - `whale_moves`
   - `unified_odds`
   - `ev_signals`
   - `props_live`
4. Add migration notes for data repair operations currently embedded in app startup.

## Immediate Tracking

- Keep `main.py` startup DDL enabled during transition to avoid downtime.
- Introduce `ENABLE_STARTUP_DDL` gate (default true) so migration-only environments can disable and validate cleanly.
- Require each startup DDL block to have a matching Alembic issue/task for removal.

