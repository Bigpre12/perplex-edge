import axios from 'axios';
import { TOKEN_STORAGE_KEY, handleUnauthorized } from './authStorage';
const isServer = typeof window === 'undefined';
const env = isServer ? (globalThis as any).process?.env : {};
export const API_BASE = isServer 
  ? (env?.NEXT_PUBLIC_API_URL || 'https://perplex-edge-backend-copy-production.up.railway.app')
  : '/backend';
const API_URL = isServer 
  ? (env?.NEXT_PUBLIC_API_URL || 'https://perplex-edge-backend-copy-production.up.railway.app')
  : '/backend';
export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});
// Automatically inject JWT token from localStorage into every request
api.interceptors.request.use((config: any) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem(TOKEN_STORAGE_KEY);
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
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
    decisions: async (sport?: string) => {
      try {
        const { data } = await api.get(sport ? `/api/brain/decisions?sport=${sport}` : '/api/brain/decisions');
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
      const { data } = await api.get('/api/health');
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
  adminStats: async (email: string) => {
    try {
      const { data } = await api.get(`/api/admin/stats?email=${email}`);
      return data;
    } catch (err) { return handleApiError(err); }
  }
};
export default API;
