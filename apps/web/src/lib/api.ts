import toast from "react-hot-toast";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const WS_BASE_URL = process.env.NEXT_PUBLIC_WS_URL || BASE_URL.replace("http", "ws");

export interface ApiResponse<T = any> {
  data: T;
  meta: {
    sport?: string;
    generated_at: string;
    freshness_ms: number;
    quota_remaining?: number;
  };
  errors: string[];
  status?: number; // Added for isApiError compatibility
  message?: string; // Added for isApiError compatibility
}

/**
 * Institutional API Circuit Breaker & Type Guard
 */
export function isApiError(obj: any): obj is { status: number; message?: string; errors?: string[] } {
  if (!obj) return false;
  return (
    typeof obj.status === "number" && (obj.status >= 400 || obj.errors?.length > 0)
  );
}

class InstitutionalApiClient {
  private async request<T>(
    endpoint: string, 
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    const url = `${BASE_URL}${endpoint}`;
    
    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          "Content-Type": "application/json",
          ...options.headers,
        },
      });

      const json = await response.json();

      // Ensure status is included in the JSON for the type guard
      if (json && typeof json === 'object') {
        json.status = response.status;
      }

      // Handle Tier Exceptions (403)
      if (response.status === 403) {
        toast.error("Upgrade to Elite for this alpha.");
        // We still return the JSON so components can handle the 403
        return json;
      }

      // Handle Authentication Exceptions (401)
      if (response.status === 401) {
        throw new Error("Unauthorized");
      }

      if (!response.ok) {
        const errorMsg = json.errors?.[0] || json.message || "Institutional API Error";
        toast.error(errorMsg);
        return json; // Return JSON even on error for component handling
      }

      return json as ApiResponse<T>;
    } catch (error: any) {
      if (error.message === "Failed to fetch") {
        toast.error("Lucrix Backend Offline");
      }
      // Return a simulated API error object instead of throwing
      return {
        data: null as any,
        meta: { generated_at: new Date().toISOString(), freshness_ms: 0 },
        errors: [error.message],
        status: 500,
        message: error.message
      };
    }
  }

  // Generic HTTP Methods
  async get<T>(endpoint: string) { return this.request<T>(endpoint, { method: "GET" }); }
  async post<T>(endpoint: string, body?: any) { 
    return this.request<T>(endpoint, { 
      method: "POST", 
      body: body ? JSON.stringify(body) : undefined 
    }); 
  }
  async put<T>(endpoint: string, body?: any) { 
    return this.request<T>(endpoint, { 
      method: "PUT", 
      body: body ? JSON.stringify(body) : undefined 
    }); 
  }
  async delete<T>(endpoint: string) { return this.request<T>(endpoint, { method: "DELETE" }); }

  // --- LEGACY & COMPATIBILITY LAYER ---
  async fetch(endpoint: string) { return this.get(endpoint); }
  async apiFetch(endpoint: string) { return this.get(endpoint); }

  // --- CORE ENGINE ENDPOINTS ---
  
  async getProps(sport: string, market?: string) {
    const params = new URLSearchParams({ sport });
    if (market) params.append("market", market);
    return this.get<any[]>(`/api/props?${params.toString()}`);
  }

  async getEV(sport?: string, minEdge: number = 2.0) {
    const params = new URLSearchParams({ min_edge: minEdge.toString() });
    if (sport) params.append("sport", sport);
    return this.get<any[]>(`/api/ev?${params.toString()}`);
  }

  async getSignals(sport?: string) {
    return this.get<any[]>(sport ? `/api/signals?sport=${sport}` : "/api/signals");
  }

  async getLive(sport?: string) {
    return this.get<any[]>(sport ? `/api/live/scoreboard?sport=${sport}` : "/api/live/scoreboard");
  }

  async getFreshness(sport?: string) {
    return this.get<any>(sport ? `/api/meta/freshness?sport=${sport}` : "/api/meta/freshness");
  }

  async getHealth() { return this.get<any>("/api/meta/health"); }
  async health() { return this.getHealth(); }

  // --- INSTITUTIONAL MODULES ---

  async adminStats(email?: string) { 
    return this.get<any>(email ? `/api/admin/stats?email=${email}` : "/api/admin/stats"); 
  }

  async arbitrage(sport: string = "NBA") { return this.get<any[]>(`/api/arbitrage?sport=${sport}`); }
  async brain(sport: string = "NBA") { return this.get<any>(`/api/brain?sport=${sport}`); }
  async brainMetrics() { return this.get<any>("/api/brain/metrics"); }
  
  async stripeCheckout(priceId: string) { 
    return this.post<any>("/api/payments/checkout", { price_id: priceId }); 
  }

  async billingPortal() { return this.get<any>("/api/payments/portal"); }
  
  async hitRateSummary() { return this.get<any>("/api/hit-rate/summary"); }
  async hitRateByPlayer() { return this.get<any>("/api/hit-rate/players"); }

  async affiliateMyLink() { return this.get<any>("/api/affiliate/link"); }
  
  async authKeys() { return this.get<any[]>("/api/auth/keys"); }
  async generateKey() { return this.post<any>("/api/auth/keys/generate"); }
  async updateWebhooks(url: string) { return this.post<any>("/api/auth/webhooks", { url }); }

  async edgeConfig() { return this.get<any>("/api/settings/edge-config"); }
  async saveEdgeConfig(config: any) { return this.post<any>("/api/settings/edge-config", config); }

  async backtestRun(params: any) { return this.post<any>("/api/strategy/backtest", params); }

  async ledgerMyBets() { return this.get<any[]>("/api/ledger/my-bets"); }
  async ledgerStats() { return this.get<any>("/api/ledger/stats"); }
  async socialShare(betId: string) { return this.post<any>(`/api/ledger/share/${betId}`); }

  async lineMovement(sport: string = "NBA") { return this.get<any[]>(`/api/line-movement?sport=${sport}`); }
  
  async getParlays() { return this.get<any[]>("/api/parlays"); }
  async performance() { return this.get<any>("/api/performance"); }
  
  async playerProfile(id: string) { return this.get<any>(`/api/players/${id}`); }
  async playerTrends(id: string) { return this.get<any>(`/api/players/${id}/trends`); }
  
  async slate(sport: string = "NBA") { return this.get<any[]>(`/api/slate?sport=${sport}`); }
  async trendHunter() { return this.get<any[]>("/api/trend-hunter"); }
  async whaleSignals(sport?: string) { 
    return this.get<any[]>(sport ? `/api/whale/signals?sport=${sport}` : "/api/whale/signals"); 
  }
  
  async trackRecordSummary() { return this.get<any>("/api/results/summary"); }
  async trackRecordRecent() { return this.get<any[]>("/api/results/recent"); }

  async aiChat(message: string) { return this.post<any>("/api/ai/chat", { message }); }
  async oracle(query: string) { return this.post<any>("/api/ai/oracle", { query }); }
  async mlPredict(params: any) { return this.post<any>("/api/ml/predict", params); }
  
  async autocopy(params: any) { return this.post<any>("/api/autocopy", params); }
  async globalSearch(query: string) { return this.get<any>(`/api/search?q=${query}`); }
  
  async authMe() { return this.get<any>("/api/auth/me"); }
  async resetCircuit() { return this.post("/api/meta/circuit-reset"); }

  // --- WEBSOCKET REGISTRY ---
  get wsBaseUrl() { return WS_BASE_URL; }
  get wsEv() { return `${WS_BASE_URL}/ws/ev`; }
  get wsKalshi() { return `${WS_BASE_URL}/ws/kalshi`; }
  get wsOdds() { return `${WS_BASE_URL}/ws/odds`; }

  // --- RECENT INTEL FLOW ---
  async recentIntel() { return this.get<any[]>("/api/intel/recent"); }
  async injuries(sport?: string) { return this.get<any[]>(sport ? `/api/intel/injuries?sport=${sport}` : "/api/intel/injuries"); }
  async sharpMoves() { return this.get<any[]>("/api/intel/sharp-moves"); }
  async evTop() { return this.get<any[]>("/api/intel/ev-top"); }

  // --- KALSHI INSTITUTIONAL ---

  async getKalshiMarkets(sport: string = "NBA") {
    return this.get<any[]>(`/api/kalshi/markets?sport=${sport}`);
  }

  async getKalshiOrderBook(ticker: string) {
    return this.get<any>(`/api/kalshi/markets/${ticker}/orderbook`);
  }

  async getKalshiHistory(ticker: string) {
    return this.get<any[]>(`/api/kalshi/markets/${ticker}/history`);
  }

  async getKalshiEvents(series?: string) {
    return this.get<any[]>(series ? `/api/kalshi/events?series=${series}` : "/api/kalshi/events");
  }

  async getKalshiEV(sport: string = "NBA") {
    return this.get<any[]>(`/api/kalshi/ev?sport=${sport}`);
  }

  async getKalshiArb(sport: string = "NBA") {
    return this.get<any[]>(`/api/kalshi/arb?sport=${sport}`);
  }

  async getKalshiPortfolio() {
    return this.get<any>("/api/kalshi/portfolio");
  }

  async placeKalshiOrder(order: { ticker: string; side: string; count: number; price: number }) {
    return this.post<any>("/api/kalshi/orders", order);
  }

  async cancelKalshiOrder(orderId: string) {
    return this.delete<any>(`/api/kalshi/orders/${orderId}`);
  }

  readonly pollMs = 30000;
}

export const api = new InstitutionalApiClient();
export const API = api; // Capitalized compatibility layer
export default api;

export const resetCircuit = () => api.resetCircuit();
export function unwrap<T>(res: ApiResponse<T>): T { return res.data; }
