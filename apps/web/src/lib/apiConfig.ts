/**
 * Lucrix API Configuration
 * Centralizes endpoint management to avoid hardcoded localhost URLs.
 */
export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

if (typeof window !== 'undefined') {
    console.info("Lucrix Edge: Standardized relative API paths active.");
}

const BASE = API_BASE_URL;
const WS_BASE = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000";

export const API_ENDPOINTS = {
    // Core (Legacy, preserved for unmigrated components)
    CHATTING: `${BASE}/api/chat/ask-oracle`,
    LEADERBOARD: `${BASE}/api/profiles/leaderboard`,
    PROFILES: `${BASE}/api/profiles`,
    AFFILIATES: `${BASE}/api/affiliates`,
    ADMIN: `${BASE}/api/admin`,
    STRIPE: `${BASE}/api/stripe`,
    PUSH: `${BASE}/api/push`,
    LEDGER: `${BASE}/api/ledger`,
    ODDS: `${BASE}/api/props/player`,
    ANTIGRAVITY: `${BASE}/api/antigravity/config`,
    LINE_MOVEMENT: `${BASE}/api/line-movement`,
    SMART_MONEY: `${BASE}/api/smart-money`,
    SUGGESTED_PARLAYS: `${BASE}/api/immediate/suggested-parlays`,
    VALIDATION_PICKS: `${BASE}/api/validation/picks`,
    BRAIN_DECISIONS: `${BASE}/api/brain/brain-decisions`,
    BRAIN_HEALTH: `${BASE}/api/brain/health`,
    MARKET_INTEL: `${BASE}/api/brain/market-intel`,
    NEWS_TICKER: `${BASE}/api/news/ticker`,
    TRACK_RECORD_RECENT: `${BASE}/api/track-record/recent`,
    TRACK_RECORD_PERFORMANCE: `${BASE}/api/track-record/performance`,
    TRACK_RECORD_SUMMARY: `${BASE}/api/track-record/summary`,
    AUTOCOPY: `${BASE}/api/copy`,
    KELLY: `${BASE}/api/kelly`,
    SGP: `${BASE}/api/sgp`,
    HEDGE: `${BASE}/api/hedge`,
    CONTESTS: `${BASE}/api/contests`,
    WEATHER: `${BASE}/api/weather`,
    REFEREE: `${BASE}/api/referees`,
    H2H: `${BASE}/api/h2h`,
    DFS: `${BASE}/api/dfs`,
    SIGNAL: `${BASE}/api/execution/signal`,

    // --- CONSUMER GRADE SCHEMA (User Requested) ---

    // Auth
    AUTH_LOGIN: `${BASE}/api/auth/login`,
    AUTH_SIGNUP: `${BASE}/api/auth/signup`,

    // Health
    HEALTH: `${BASE}/api/health`,

    // Sports Props
    NBA_PROPS: `${BASE}/api/sports/30/picks/player-props`,
    NCAAB_PROPS: `${BASE}/api/sports/39/picks/player-props`,
    WNBA_PROPS: `${BASE}/api/sports/53/picks/player-props`,
    NFL_PROPS: `${BASE}/api/sports/31/picks/player-props`,
    NCAAF_PROPS: `${BASE}/api/sports/41/picks/player-props`,
    MLB_PROPS: `${BASE}/api/sports/40/picks/player-props`,
    NHL_PROPS: `${BASE}/api/sports/22/picks/player-props`,
    ATP_PROPS: `${BASE}/api/sports/42/picks/player-props`,
    WTA_PROPS: `${BASE}/api/sports/43/picks/player-props`,
    MMA_PROPS: `${BASE}/api/sports/54/picks/player-props`,
    BOXING_PROPS: `${BASE}/api/sports/55/picks/player-props`,

    // Combos
    NBA_COMBOS: `${BASE}/api/sports/30/picks/prop-combos`,
    NCAAB_COMBOS: `${BASE}/api/sports/39/picks/prop-combos`,

    // Parlays
    NBA_PARLAY: `${BASE}/api/sports/30/picks/parlay-builder`,
    NCAAB_PARLAY: `${BASE}/api/sports/39/picks/parlay-builder`,

    // Brain / Intelligence
    BRAIN_STATUS: `${BASE}/api/brain/live-analysis`,
    BRAIN_METRICS: `${BASE}/api/brain/brain-metrics`,
    BRAIN_ANOMALIES: `${BASE}/api/brain/injury-impact`,
    BRAIN_HEATMAP: `${BASE}/api/brain/heatmap`,
    BRAIN_INSIGHTS: `${BASE}/api/brain/brain-insights`,
    STEAM_ALERTS: `${BASE}/api/signals/alerts`,

    // Antigravity
    AG_CONFIG: `${BASE}/api/antigravity/config`,
    AG_WORKING_PROPS: `${BASE}/api/immediate/working-player-props`,
    AG_PARLAYS: `${BASE}/api/immediate/working-parlays`,
    AG_MONTE_CARLO: `${BASE}/api/immediate/monte-carlo`,

    // CLV & Analytics
    CLV_LEADERBOARD: `${BASE}/api/clv/leaderboard`,
    ANALYTICS_DASH: `${BASE}/api/analytics/dashboard`,
    MODEL_PERFORMANCE: `${BASE}/api/analytics/model-performance`,
    RESULTS_PUBLIC: `${BASE}/api/results/public`,

    // Ledger
    LEDGER_MY_BETS: `${BASE}/api/ledger/my-bets`,
    LEDGER_STATS: `${BASE}/api/ledger/stats`,

    // ML
    ML_PREDICT: `${BASE}/api/ml/predict-probability`,

    // AI
    AI_CHAT: `${BASE}/api/ai/chat`,
    ORACLE_CHAT: `${BASE}/api/oracle/chat`,
    REPORTING_EXPORT: `${BASE}/api/reporting/export`,

    // Social
    SHARE: `${BASE}/api/share`,
    SOCIAL_SHARE: `${BASE}/api/social/share`,

    // User
    USER_PREFERENCES: `${BASE}/api/user/preferences`,

    // Admin
    ADMIN_GRANT: `${BASE}/api/admin/grant-access`,
    ADMIN_REVOKE: `${BASE}/api/admin/revoke-access`,
    ADMIN_LIST: `${BASE}/api/admin/access-list`,
    ADMIN_AG_CONFIG: `${BASE}/api/antigravity/config`,

    // WebSocket
    WS_ODDS: `${WS_BASE}/api/ws/live-odds`,
    WS_PROPS: `${WS_BASE}/api/ws/props`,

    // Institutional Suite
    PICKS: `${BASE}/api/picks`,
    BIT_RATES: `${BASE}/api/picks/hit-rates`,
    ARBITRAGE: `${BASE}/api/arbitrage`,
    EDGES: `${BASE}/api/edges/top`,
    SLATE: `${BASE}/api/slate/today`,
    PLAYER_PROFILE: (name: string) => `${BASE}/api/players/${encodeURIComponent(name)}`,
} as const;

export const API = API_ENDPOINTS;

// Type helper for autocomplete
export type ApiEndpointKey = keyof typeof API_ENDPOINTS;

// Helper — build sport-specific URL dynamically
export function sportAPI(sportId: number) {
    return {
        props: `${BASE}/api/sports/${sportId}/picks/player-props`,
        combos: `${BASE}/api/sports/${sportId}/picks/prop-combos`,
        parlay: `${BASE}/api/sports/${sportId}/picks/parlay-builder`,
        lines: `${BASE}/api/sports/${sportId}/picks/game-lines`,
        games: `${BASE}/api/sports/${sportId}/games`,
    }
}
