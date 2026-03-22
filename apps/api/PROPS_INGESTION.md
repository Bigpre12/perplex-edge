# Props Ingestion Lifecycle

This document describes how player props are ingested, processed, and surfaced in the Perplex Edge platform.

## Overview

The props ingestion layer is integrated into the `UnifiedIngestionService`. It runs every 5 minutes per sport and is responsible for fetching live pricing from The Odds API and normalizing it into the `props_live` table.

## Ingestion Flow

1.  **Event Discovery**: Fetches upcoming events for the target sport.
2.  **Pricing Retrieval**: Fetches standard odds (H2H, Spreads, Totals) and iterates through the top 20 upcoming events to fetch deep player prop markets.
3.  **Normalization**: The `OddsMapper` groups separate Over/Under outcomes from multiple bookmakers into unified `PropRecord` objects.
4.  **Enrichment**: Records are enriched with:
    - **Market Intelligence**: Identifying "Best Odds" for Over/Under.
    - **Book Categorization**: Flagging "Sharp" (e.g., Pinnacle, Bookmaker.eu) vs "Soft" books.
    - **Confidence**: A heuristic score based on book coverage for a specific line.
5.  **Persistence Strategy**:
    - **Cleanup**: Existing `props_live` rows for the current sport are cleared before the new batch is inserted.
    - **Upsert**: New records are upserted into `props_live` (Live UI data).
    - **Archive**: Snapshots are appended to `props_history` for later Closing Line Value (CLV) analysis.
6.  **Brain Integration**: Records are synced to the `unified_odds` table to trigger the EV Engine and other predictive models.

## Data Model

- **Table**: `props_live`
- **Unique Constraint**: `(sport, game_id, player_name, market_key, book)`
- **Core Models**: `PropLive` (models/brain.py), `PropRecord` (schemas/props.py)

## Adding New Sports

To enable props for a new sport, add the sport key and its supported markets to the `PROP_MARKETS_BY_SPORT` dictionary in `apps/api/src/services/unified_ingestion.py`.
