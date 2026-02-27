/**
 * Perplex Edge API Configuration
 * Centralizes endpoint management to avoid hardcoded localhost URLs.
 */

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const API_ENDPOINTS = {
    CHATTING: `${API_BASE_URL}/api/chat/ask-oracle`,
    LEADERBOARD: `${API_BASE_URL}/api/profiles/leaderboard`,
    PROFILES: `${API_BASE_URL}/api/profiles`,
    AFFILIATES: `${API_BASE_URL}/api/affiliates`,
    ADMIN: `${API_BASE_URL}/api/admin`,
    STRIPE: `${API_BASE_URL}/api/stripe`,
    PUSH: `${API_BASE_URL}/api/push`,
    LEDGER: `${API_BASE_URL}/api/ledger`,
    ODDS: `${API_BASE_URL}/immediate/working-player-props`,
    KELLY: `${API_BASE_URL}/api/kelly`,
    SGP: `${API_BASE_URL}/api/sgp`,
    HEDGE: `${API_BASE_URL}/api/hedge`,
    CONTESTS: `${API_BASE_URL}/api/contests`,
    WEATHER: `${API_BASE_URL}/weather`,
    REFEREE: `${API_BASE_URL}/referees`,
    H2H: `${API_BASE_URL}/h2h`,
    DFS: `${API_BASE_URL}/dfs`,
    LINE_MOVEMENT: `${API_BASE_URL}/line-movement`,
    WS_ODDS: API_BASE_URL.replace('http', 'ws') + '/api/ws/live-odds'
};
