import { SportKey } from './sports.config';

const BASE = (process.env.EXPO_PUBLIC_API_URL || 'http://192.168.1.64:3300').replace(/\/$/, '');

export const API = {
    health: () => `${BASE}/health`,
    props: (sport: SportKey) => `${BASE}/api/props?sport=${sport}`,
    propsByPlayer: (sport: SportKey, name: string) => `${BASE}/api/props/players/${encodeURIComponent(name)}`,
    hitRates: (sport: SportKey) => `${BASE}/api/analytics/hit-rate/summary?sport=${sport}`,
    bestProps: (sport: SportKey) => `${BASE}/api/props/best?sport=${sport}`,
    odds: (sport: SportKey) => `${BASE}/api/props?sport=${sport}`, // Map to props as it contains odds
    lineMovement: (sport: SportKey) => `${BASE}/api/live/line-movement?sport=${sport}`,
    rlm: (sport: SportKey) => `${BASE}/api/live/line-movement?sport=${sport}`,
    player: (sport: SportKey) => `${BASE}/api/props/players`,
    playerStats: (sport: SportKey, name: string) => `${BASE}/api/props/players/${encodeURIComponent(name)}`,
    injuries: (sport: SportKey) => `${BASE}/api/intel/injuries?sport=${sport}`,
    roster: (sport: SportKey) => `${BASE}/api/intel/roster?sport=${sport}`,
    brainDecisions: (sport: SportKey, limit = 5) => `${BASE}/api/brain/brain-decisions?sport=${sport}&limit=${limit}`,
    brainMetrics: (sport: SportKey) => `${BASE}/api/brain/brain-metrics?sport=${sport}`,
    brainInsights: (sport: SportKey) => `${BASE}/api/brain/brain-insights?sport=${sport}`,
    alerts: (sport: SportKey) => `${BASE}/api/signals/steam?sport=${sport}`,
    recentIntel: (sport: SportKey) => `${BASE}/api/intel/recent-intel?sport=${sport}`,
    news: (sport: SportKey) => `${BASE}/api/news/ticker?sport=${sport}`,
    activeMoves: (sport: SportKey) => `${BASE}/api/signals/whale?sport=${sport}`,
    sharpMoney: (sport: SportKey) => `${BASE}/api/signals/sharp?sport=${sport}`,
    publicBetting: (sport: SportKey) => `${BASE}/api/signals/whale?sport=${sport}`, // Closest match
    parlayBuild: () => `${BASE}/api/props/parlay/build`,
    parlayValidate: () => `${BASE}/api/props/parlay/validate`,
    parlayHistory: () => `${BASE}/api/parlay/history`,
};

// ─── Circuit Breaker ──────────────────────────────────────────────────────────
let circuitOpen = false;
let circuitFailures = 0;
let circuitResetTimer: ReturnType<typeof setTimeout> | null = null;
const CIRCUIT_THRESHOLD = 5;
const CIRCUIT_RESET_MS = 30_000;

function tripCircuit() {
    circuitOpen = true;
    circuitFailures = 0;
    console.warn("[API] Circuit breaker OPEN — pausing requests for 30s");
    if (circuitResetTimer) clearTimeout(circuitResetTimer);
    circuitResetTimer = setTimeout(() => {
        circuitOpen = false;
        console.info("[API] Circuit breaker RESET — resuming requests");
    }, CIRCUIT_RESET_MS);
}

export function resetCircuit() {
    circuitOpen = false;
    circuitFailures = 0;
    if (circuitResetTimer) clearTimeout(circuitResetTimer);
    console.info("[API] Circuit breaker manually reset");
}

export function isCircuitOpen() {
    return circuitOpen;
}

// ─── Types ────────────────────────────────────────────────────────────────────
export interface ApiError {
    error: true;
    message: string;
    status?: number;
    offline?: boolean;
}

export type ApiResult<T> = T | ApiError;

export function isApiError(val: unknown): val is ApiError {
    return typeof val === "object" && val !== null && (val as ApiError).error === true;
}

// ─── Options ──────────────────────────────────────────────────────────────────
interface FetchOptions extends RequestInit {
    retries?: number;
    retryDelay?: number;
    token?: string;
    /** If true, returns ApiError object instead of throwing. Default: true */
    safe?: boolean;
}

// ─── Core Fetch ───────────────────────────────────────────────────────────────
export async function apiFetch<T>(
    endpoint: string,
    options: FetchOptions = {}
): Promise<ApiResult<T>> {
    const { retries = 2, retryDelay = 500, token, safe = true, ...fetchOptions } = options;

    // Circuit open — return error object, never throw
    if (circuitOpen) {
        console.warn(`[API] Circuit open — skipping ${endpoint}`);
        return { error: true, message: "Backend offline. Circuit breaker is open.", offline: true };
    }

    const url = endpoint.startsWith("http") ? endpoint : `${BASE}${endpoint}`;

    const headers: Record<string, string> = {
        "Content-Type": "application/json",
        ...(fetchOptions.headers as Record<string, string>),
    };

    if (token) headers["Authorization"] = `Bearer ${token}`;

    let lastError: ApiError = { error: true, message: "Unknown error" };

    for (let attempt = 0; attempt <= retries; attempt++) {
        try {
            const controller = new AbortController();
            const timeout = setTimeout(() => controller.abort(), 10_000);

            const res = await fetch(url, {
                ...fetchOptions,
                headers,
                signal: controller.signal,
            });

            clearTimeout(timeout);

            if (!res.ok) {
                const body = await res.text().catch(() => "");
                const errMsg = `HTTP ${res.status} ${res.statusText} — ${endpoint} — ${body}`;
                console.error(`[API] ${errMsg}`);
                lastError = { error: true, message: errMsg, status: res.status };

                // Don't retry 4xx
                if (res.status >= 400 && res.status < 500) break;
                continue;
            }

            circuitFailures = 0; // success — reset counter
            return res.json() as Promise<T>;

        } catch (err: unknown) {
            const e = err instanceof Error ? err : new Error(String(err));

            if (e.name === "AbortError") {
                console.error(`[API] Timeout on attempt ${attempt + 1}: ${url}`);
                lastError = { error: true, message: `Request timed out: ${endpoint}` };
            } else if (
                e.message.includes("Failed to fetch") ||
                e.message.includes("ERR_CONNECTION_REFUSED") ||
                e.message.includes("NetworkError") ||
                e.message.includes("Load failed")
            ) {
                console.error(`[API] Network failure attempt ${attempt + 1}: ${url} — backend running on ${BASE}?`);
                lastError = { error: true, message: "Backend offline", offline: true };
                circuitFailures++;
                if (circuitFailures >= CIRCUIT_THRESHOLD) {
                    tripCircuit();
                    // Return immediately — no point retrying with circuit open
                    return lastError;
                }
            } else {
                console.error(`[API] Fetch error attempt ${attempt + 1}: ${url}`, e.message);
                lastError = { error: true, message: e.message };
            }

            if (attempt < retries) {
                await new Promise((r) => setTimeout(r, retryDelay * (attempt + 1)));
            }
        }
    }

    // safe mode: return error object — never throw into React render
    if (safe) return lastError;
    throw new Error(lastError.message);
}

// ─── Convenience Methods ──────────────────────────────────────────────────────
export const api = {
    get: <T>(endpoint: string, opts?: FetchOptions) =>
        apiFetch<T>(endpoint, { method: "GET", ...opts }),

    post: <T>(endpoint: string, body: unknown, opts?: FetchOptions) =>
        apiFetch<T>(endpoint, {
            method: "POST",
            body: JSON.stringify(body),
            ...opts,
        }),

    put: <T>(endpoint: string, body: unknown, opts?: FetchOptions) =>
        apiFetch<T>(endpoint, {
            method: "PUT",
            body: JSON.stringify(body),
            ...opts,
        }),

    patch: <T>(endpoint: string, body: unknown, opts?: FetchOptions) =>
        apiFetch<T>(endpoint, {
            method: "PATCH",
            body: JSON.stringify(body),
            ...opts,
        }),

    delete: <T>(endpoint: string, opts?: FetchOptions) =>
        apiFetch<T>(endpoint, { method: "DELETE", ...opts }),

    // Named domain helpers — used by /live, /sharp, etc.
    live: <T>(endpoint: string, opts?: FetchOptions) =>
        apiFetch<T>(endpoint, { method: "GET", ...opts }),

    sharp: <T>(endpoint: string, opts?: FetchOptions) =>
        apiFetch<T>(endpoint, { method: "GET", ...opts }),

    props: <T>(endpoint: string, opts?: FetchOptions) =>
        apiFetch<T>(endpoint, { method: "GET", ...opts }),
};

// ─── Health Check ─────────────────────────────────────────────────────────────
export async function checkBackendHealth(): Promise<boolean> {
    const result = await apiFetch("/health", { retries: 0 });
    return !isApiError(result);
}

export default api;
