import axios from 'axios';
import { TOKEN_STORAGE_KEY, handleUnauthorized } from './authStorage';
const isServer = typeof window === 'undefined';

// --- CONFIGURATION ---
const PROD_URL = "https://perplex-edge-backend-copy-production.up.railway.app";
const LOCAL_URL = "http://localhost:8000";

// On server, we need the full URL. On client, we use the /backend proxy for better CORS/SSL support.
const rawUrl = (typeof process !== 'undefined' ? process.env.NEXT_PUBLIC_API_URL : null) || PROD_URL;
let configuredUrl = rawUrl;

// Sanity check: Ensure we don't use localhost in production mode on the server
if (isServer && process.env.NODE_ENV === "production" && configuredUrl.includes("localhost")) {
    configuredUrl = PROD_URL;
}

export const API_BASE = isServer ? configuredUrl : "/backend";
const API_URL = isServer ? configuredUrl : "/backend";

// WebSocket Base URL: swapping http -> ws, https -> wss
const wsBase = isServer ? configuredUrl : window.location.origin;
export const WS_BASE = wsBase.replace('https://', 'wss://').replace('http://', 'ws://');
export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Implementation of exponential backoff retry logic (Phase 1)
api.interceptors.response.use(
  (response) => response,
  async (error: any) => {
    const config = error.config;
    if (!config) return Promise.reject(error);

    // Initialize retry count
    config._retryCount = config._retryCount || 0;

    // Only retry on network errors or 5xx server errors
    const isNetworkError = !error.response;
    const isServerError = error.response && error.response.status >= 500 && error.response.status <= 599;

    // Check for circuit breaker or auth errors specifically - DO NOT retry these
    const errorMessage = error?.response?.data?.error || '';
    const isAuthRelatedError = error.response && (error.response.status === 401 || error.response.status === 403);
    const isCircuitBreakerError = errorMessage.includes('Circuit breaker') || errorMessage.includes('authentication');

    if ((isNetworkError || isServerError) && !isAuthRelatedError && !isCircuitBreakerError && config._retryCount < 3) {
      config._retryCount += 1;
      
      // Exponential backoff: 1s, 2s, 4s
      const backoffDelay = Math.pow(2, config._retryCount - 1) * 1000;
      console.warn(`[API Retry] ${config.url} failed. Attempt ${config._retryCount}/3 in ${backoffDelay}ms...`);
      
      await new Promise(resolve => setTimeout(resolve, backoffDelay));
      return api(config);
    }
    
    return Promise.reject(error);
  }
);

// Automatically inject JWT token from localStorage or environment key into every request
api.interceptors.request.use((config: any) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem(TOKEN_STORAGE_KEY) || process.env.NEXT_PUBLIC_API_KEY;
    if (token) {
      // Ensure strictly Bearer format
      config.headers.Authorization = token.startsWith('Bearer ') ? token : `Bearer ${token}`;
    }

    // Dev-only warning for missing auth header
    if (process.env.NODE_ENV === 'development' && !config.headers.Authorization && !config.url?.includes('/api/auth/')) {
        console.warn('[API] Missing auth header on', config.url);
    }
  }
  return config;
}, (error: any) => {
  return Promise.reject(error);
});
// Automatically handle 401 Unauthorized by clearing session and redirecting
// But NOT on auth pages (login, signup, etc.) to prevent redirect loops
api.interceptors.response.use((response: any) => {
  return response;
}, (error: any) => {
  const AUTH_PATHS = ['/login', '/signup', '/forgot-password', '/reset-password'];
  const isOnAuthPage = typeof window !== 'undefined' && AUTH_PATHS.some(p => window.location.pathname.startsWith(p));
  if (error.response && error.response.status === 401 && !isOnAuthPage) {
    console.warn('Authentication expired (401). Clearing session and redirecting...');
    handleUnauthorized();
  }
  return Promise.reject(error);
});
// Augment the axios instance with methods expected by various components
(api as any).auth = {
  login: async (credentials: any) => {
    const { data } = await api.post('/api/auth/login', credentials);
    return data;
  },
  signup: async (userData: any) => {
    const { data } = await api.post('/api/auth/signup', userData);
    return data;
  },
  forgotPassword: async (payload: any) => {
    const { data } = await api.post('/api/auth/forgot-password', payload);
    return data;
  },
  resetPassword: async (payload: any) => {
    const { data } = await api.post('/api/auth/reset-password', payload);
    return data;
  }
};
(api as any).adminStats = async (email: string) => {
  const { data } = await api.get(`/api/admin/stats?email=${email}`);
  return data;
};
(api as any).simulate = async (legs: any[], sims = 100, trials = 10000) => {
  const { data } = await api.post('/api/parlays/simulate', { legs, n_sims: trials });
  return data;
};
(api as any).buildParlay = async (sport: string) => {
  const { data } = await api.get(`/api/oracle/build-parlay`, { params: { sport } });
  return data;
};
(api as any).ledgerMyBets = async () => {
  const { data } = await api.get('/api/bets/my');
  return data;
};
(api as any).ledgerStats = async () => {
  const { data } = await api.get('/api/bets/stats');
  return data;
};
(api as any).ledgerCreateBet = async (betData: any) => {
  const { data } = await api.post('/api/bets', betData);
  return data;
};
(api as any).socialShare = async (shareData: any) => {
  const { data } = await api.post('/api/social/share', shareData);
  return data;
};
// Helper for error handling
export const handleApiError = (error: any) => {
  console.error('API Error:', error.response?.data || error.message);
  return error.response?.data || { detail: 'An unexpected error occurred' };
};
export const isApiError = (data: any) => {
  return !data || data.detail || data.error || data.message === 'error';
};
export const unwrap = (d: any): any[] => {
  if (!d) return [];
  if (Array.isArray(d)) return d;
  const nested = d.data || d.results || d.items || d.props || d.games || d.edges || d.alerts || d.injuries || d.decisions || d.news || d.moves || [];
  return Array.isArray(nested) ? nested : [];
};
// Legacy API methods needed by dashboard and hooks
export const API = {
  auth: {
    login: async (credentials: any) => {
      try {
        const { data } = await api.post('/api/auth/login', credentials);
        return data;
      } catch (err) {
        return handleApiError(err);
      }
    },
    signup: async (userData: any) => {
      try {
        const { data } = await api.post('/api/auth/signup', userData);
        return data;
      } catch (err) {
        return handleApiError(err);
      }
    },
    forgotPassword: async (payload: any) => {
      try {
        const { data } = await api.post('/api/auth/forgot-password', payload);
        return data;
      } catch (err) {
        return handleApiError(err);
      }
    },
    resetPassword: async (payload: any) => {
      try {
        const { data } = await api.post('/api/auth/reset-password', payload);
        return data;
      } catch (err) {
        return handleApiError(err);
      }
    }
  },
  brain: {
    status: async () => {
      try {
        const { data } = await api.get('/api/brain');
        return data;
      } catch (err) { return handleApiError(err); }
    },
    decisions: async (sport?: string, limit?: number) => {
      try {
        const params: any = {};
        if (sport) params.sport = sport;
        if (limit) params.limit = limit;
        const { data } = await api.get('/api/brain/decisions', { params });
        return data;
      } catch (err) { return handleApiError(err); }
    },
    metrics: async () => {
      try {
        const { data } = await api.get('/api/brain/metrics');
        return data;
      } catch (err) { return handleApiError(err); }
    }
  },
  ev: {
    top: async (sport?: string, limit = 10) => {
      try {
        const { data } = await api.get(`/api/ev/top?sport=${sport || ''}&limit=${limit}`);
        return data;
      } catch (err) { return handleApiError(err); }
    },
    scanner: async (sport?: string) => {
      try {
        const { data } = await api.get(`/api/ev?sport=${sport || ''}`);
        return data;
      } catch (err) { return handleApiError(err); }
    }
  },
  signals: {
    freshness: async (sport?: string) => {
      try {
        const { data } = await api.get(`/api/signals/freshness?sport=${sport || ''}`);
        return data;
      } catch (err) { return handleApiError(err); }
    }
  },
  props: async (sport?: string) => {
    try {
      const { data } = await api.get(sport ? `/api/props/graded?sport=${sport}` : '/api/props/graded');
      return data;
    } catch (err) { return handleApiError(err); }
  },
  propsScored: async (sport?: string, limit = 50) => {
    try {
      const { data } = await api.get(`/api/props/scored?sport=${sport || ''}&limit=${limit}`);
      return data;
    } catch (err) { return handleApiError(err); }
  },
  injuries: async (sport?: string) => {
    try {
      const { data } = await api.get(sport ? `/api/injuries?sport=${sport}` : '/api/injuries');
      return data;
    } catch (err) { return handleApiError(err); }
  },
  news: async (sport?: string) => {
    try {
      const { data } = await api.get(sport ? `/api/news?sport=${sport}` : '/api/news');
      return data;
    } catch (err) { return handleApiError(err); }
  },
  lineMovement: async (sport?: string) => {
    try {
      const { data } = await api.get(sport ? `/api/line-movement?sport=${sport}` : '/api/line-movement');
      return data;
    } catch (err) { return handleApiError(err); }
  },
  health: async () => {
    try {
      const { data } = await api.get('/api/health', { params: { t: Date.now() } });
      return data;
    } catch (err) { return handleApiError(err); }
  },
  metrics: async () => {
    try {
      const { data } = await api.get('/api/brain/metrics');
      return data;
    } catch (err) { return handleApiError(err); }
  },
  brainMetrics: async () => {
    try {
      const { data } = await api.get('/api/brain/metrics');
      return data;
    } catch (err) { return handleApiError(err); }
  },
  recentIntel: async (sport?: string) => {
    try {
      const { data } = await api.get(sport ? `/api/intel?sport=${sport}` : '/api/intel');
      return data;
    } catch (err) { return handleApiError(err); }
  },
  alerts: async (sport?: string) => {
    try {
      const { data } = await api.get(sport ? `/api/alerts?sport=${sport}` : '/api/alerts');
      return data;
    } catch (err) {
      return { alerts: [], total: 0, status: 'unavailable', sport: sport || 'all' };
    }
  },
  authMe: async () => {
    try {
      const { data } = await api.get('/api/auth/me');
      return data;
    } catch (err) { return handleApiError(err); }
  },
  referrals: async () => {
    try {
      const { data } = await api.get('/api/referrals');
      return data;
    } catch (err) { return handleApiError(err); }
  },
  hero: async (playerName: string, sport: string) => {
    try {
      const { data } = await api.get('/api/hero', { params: { name: playerName, sport } });
      return data;
    } catch (err) { return handleApiError(err); }
  },
  whale: async (sport?: string, minUnits = 0) => {
    try {
      const { data } = await api.get(`/api/whale`, { params: { sport, min_units: minUnits } });
      return data;
    } catch (err) { return handleApiError(err); }
  },
  activeMoves: async (sport?: string) => {
    try {
      const { data } = await api.get(sport ? `/api/alerts?sport=${sport}` : '/api/alerts');
      return data?.alerts || data || [];
    } catch (err) { return []; }
  },
  evTop: async (sport?: string, limit = 10) => {
    try {
      const { data } = await api.get(`/api/ev?sport=${sport || ''}&limit=${limit}`);
      return data;
    } catch (err) { return handleApiError(err); }
  },
  sharpMoves: async (sport?: string) => {
    try {
      const { data } = await api.get(sport ? `/api/alerts?sport=${sport}` : '/api/alerts');
      return data;
    } catch (err) {
      return { alerts: [], total: 0, status: 'unavailable' };
    }
  },
  hitRateSummary: async (sport?: string) => {
    try {
      const { data } = await api.get(sport ? `/api/hit-rate?sport=${sport}` : '/api/hit-rate');
      return data;
    } catch (err) { return handleApiError(err); }
  },
  playerTrends: async (playerName: string, statType: string) => {
    try {
      const { data } = await api.get(`/api/props/history`, {
        params: { player_name: playerName, market_key: statType, sport: 'basketball_nba', book: 'draftkings' }
      });
      return { history: data };
    } catch (err) { return { history: [] }; }
  },
  mlPredict: async (payload: any) => {
    try {
      const { data } = await api.post(`/api/oracle/analyze-prop`, payload);
      return data;
    } catch (err) { return handleApiError(err); }
  },
  buildParlay: async (sport: string) => {
    try {
      const { data } = await api.get(`/api/oracle/build-parlay`, { params: { sport } });
      return data;
    } catch (err) { return handleApiError(err); }
  },
  ledgerStats: async () => {
    try {
      const { data } = await api.get('/api/bets/stats');
      return data;
    } catch (err) { return handleApiError(err); }
  },
  backtestRun: async (payload: any) => {
    try {
      const { data } = await api.post('/api/backtest', payload);
      return data;
    } catch (err) { return handleApiError(err); }
  },
  reportingExport: (format: string) => {
    return `${API_BASE}/api/reporting/export?format=${format}`;
  },
  playerProfile: async (playerName: string) => {
    try {
      const { data } = await api.get('/api/hero', { params: { name: playerName, sport: 'basketball_nba' } });
      return data;
    } catch (err) { return handleApiError(err); }
  },
  wsBaseUrl: isServer ? WS_BASE : (window.location.origin.replace('http', 'ws') + '/backend'),
  wsOdds: (isServer ? WS_BASE : (typeof window !== 'undefined' ? window.location.origin.replace('http', 'ws') + '/backend' : '')) + '/api/ev/ws',
  wsKalshi: (isServer ? WS_BASE : (typeof window !== 'undefined' ? window.location.origin.replace('http', 'ws') + '/backend' : '')) + '/api/kalshi/ws',
  wsEv: isServer ? WS_BASE : (typeof window !== 'undefined' ? window.location.origin.replace('http', 'ws') + '/backend' : ''),
  pollMs: 15000,
  adminStats: async (email: string) => {
    try {
      const { data } = await api.get(`/api/admin/stats?email=${email}`);
      return data;
    } catch (err) { return handleApiError(err); }
  },
  steamAlerts: async (sport?: string) => {
    try {
      const { data } = await api.get(sport ? `/api/steam?sport=${sport}` : '/api/steam');
      return data;
    } catch (err) { return handleApiError(err); }
  },
  search: async (q: string) => {
    try {
      const { data } = await api.get('/api/search', { params: { q } });
      return data;
    } catch (err) { return handleApiError(err); }
  },
  simulate: async (legs: any[], nSims = 100, trials = 10000) => {
    try {
      const { data } = await api.post('/api/parlays/simulate', { legs, n_sims: trials });
      return data;
    } catch (err) { return handleApiError(err); }
  },
  getProps: async (sport?: string, limit = 25) => {
    try {
      const { data } = await api.get(`/api/props/graded?sport=${sport || ''}&limit=${limit}`);
      return data;
    } catch (err) { return handleApiError(err); }
  },
  me: async () => {
    try {
      const { data } = await api.get('/api/auth/me');
      return data;
    } catch (err) { return handleApiError(err); }
  },
  metaHealth: async () => {
    try {
      const { data } = await api.get('/api/meta/health');
      return data;
    } catch (err) { return handleApiError(err); }
  },
  bets: async () => {
    try {
      const { data } = await api.get('/api/bets/my');
      return data;
    } catch (err) { return handleApiError(err); }
  },
  settleBet: async (betId: number, result: string) => {
    try {
      const { data } = await api.post(`/api/bets/${betId}/settle`, { result });
      return data;
    } catch (err) { return handleApiError(err); }
  },
  clvLeaderboard: async (sport?: string) => {
    try {
      const { data } = await api.get('/api/clv/summary', { params: { sport } });
      return data;
    } catch (err) { return handleApiError(err); }
  },
  aiChat: async (message: string, context?: any) => {
    try {
      const { data } = await api.post('/api/oracle/chat', { message, context });
      return data;
    } catch (err) { return handleApiError(err); }
  },
  middleBoost: async (sport?: string) => {
    try {
      const { data } = await api.get('/api/middle-boost', { params: { sport } });
      return data;
    } catch (err) { return handleApiError(err); }
  },
  trendHunter: async (sport?: string, timeframe?: string) => {
    try {
      const { data } = await api.get('/api/props/history', { params: { sport, timeframe } });
      return data;
    } catch (err) { return handleApiError(err); }
  },
  affiliateMyLink: async (userId?: string | number) => {
    try {
      const { data } = await api.get('/api/referrals/my-link', { params: userId ? { user_id: userId } : {} });
      return data;
    } catch (err) { return handleApiError(err); }
  },
  authKeys: async () => {
    try {
      const { data } = await api.get('/api/auth/keys');
      return data;
    } catch (err) { return handleApiError(err); }
  },
  generateKey: async (label: string) => {
    try {
      const { data } = await api.post('/api/auth/keys', { label });
      return data;
    } catch (err) { return handleApiError(err); }
  },
  updateWebhooks: async (webhookData: any) => {
    try {
      const { data } = await api.post('/api/settings/webhooks', webhookData);
      return data;
    } catch (err) { return handleApiError(err); }
  },
  edgeConfig: async () => {
    try {
      const { data } = await api.get('/api/settings/edge-config');
      return data;
    } catch (err) { return handleApiError(err); }
  },
  saveEdgeConfig: async (config: any) => {
    try {
      const { data } = await api.post('/api/settings/edge-config', config);
      return data;
    } catch (err) { return handleApiError(err); }
  },
  evBoard: async (sport?: string, minEv?: number) => {
    try {
      const params: any = { sport: sport || '' };
      if (minEv !== undefined) params.min_ev = minEv;
      const { data } = await api.get('/api/ev', { params });
      return data;
    } catch (err) { return handleApiError(err); }
  },
  trackRecordSummary: async () => {
    try {
      const { data } = await api.get('/api/hit-rate/summary');
      return data;
    } catch (err) { return handleApiError(err); }
  },
  trackRecordRecent: async (limit = 20) => {
    try {
      const { data } = await api.get(`/api/bets/recent?limit=${limit}`);
      return data;
    } catch (err) { return handleApiError(err); }
  },
  stripeCheckout: async (priceId: string) => {
    try {
      const { data } = await api.post('/api/stripe/checkout', { price_id: priceId });
      return data;
    } catch (err) { return handleApiError(err); }
  },
  billing: {
    createPortalSession: async () => {
      try {
        const { data } = await api.post('/api/billing/portal');
        return data;
      } catch (err) { return handleApiError(err); }
    }
  },
  autocopy: async (endpoint: string, ids?: any[]) => {
    try {
      const { data } = await api.post(`/api/bets/${endpoint}`, { ids });
      return data;
    } catch (err) { return handleApiError(err); }
  },
  share: () => `${API_BASE}/api/social/share`,
};
export default API;
