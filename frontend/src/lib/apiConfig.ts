/**
 * Lucrix API Configuration
 * Centralizes endpoint management to avoid hardcoded localhost URLs.
 */
export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const BASE = API_BASE_URL;
const WS_BASE = API_BASE_URL.replace('https', 'wss').replace('http', 'ws');

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
    ODDS: `${BASE}/api/immediate/working-player-props`,
    ANTIGRAVITY: `${BASE}/api/antigravity/config`,
    LINE_MOVEMENT: `${BASE}/api/line-movement`,
    SMART_MONEY: `${BASE}/api/smart-money`,
    SUGGESTED_PARLAYS: `${BASE}/api/immediate/suggested-parlays`,
    VALIDATION_PICKS: `${BASE}/api/validation/picks`,
    BRAIN_DECISIONS: `${BASE}/api/immediate/brain-decisions`,
    BRAIN_HEALTH: `${BASE}/api/immediate/brain-healing-status`,
    MARKET_INTEL: `${BASE}/api/immediate/market-intel`,
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
    BRAIN_STATUS: `${BASE}/api/immediate/brain-status`,
    BRAIN_METRICS: `${BASE}/api/immediate/brain-metrics`,
    BRAIN_ANOMALIES: `${BASE}/api/immediate/brain-anomalies`,
    STEAM_ALERTS: `${BASE}/api/immediate/steam-alerts`,

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
