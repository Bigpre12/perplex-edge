import { API_BASE } from "./apiConfig";
import { TOKEN_STORAGE_KEY, handleUnauthorized } from "./authStorage";

/**
 * Standardized API Client for LUCRIX.
 * Handles auth headers, retries, and type-safe responses.
 */
interface RequestOptions extends RequestInit {
  params?: Record<string, string | number | boolean | undefined>;
  retries?: number;
  backoff?: number;
}

export class APIError extends Error {
  constructor(public status: number, public message: string, public data?: any) {
    super(message);
    this.name = "APIError";
  }
}

async function delay(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

const AUTH_PATHS = ['/login', '/signup', '/forgot-password', '/reset-password'];
function isOnAuthPage(): boolean {
  return typeof window !== 'undefined' && AUTH_PATHS.some(p => window.location.pathname.startsWith(p));
}

/**
 * Core request wrapper with retry logic and auth.
 */
export async function apiClient<T>(
  endpoint: string,
  options: RequestOptions = {}
): Promise<T> {
  const { params, retries = 3, backoff = 1000, ...fetchOptions } = options;
  // 1. Construct URL with query params
  const baseUrl = typeof window !== "undefined"
    ? window.location.origin
    : (process.env.NEXT_PUBLIC_API_URL || "https://perplex-edge-backend-copy-production.up.railway.app");

  const url = new URL(endpoint.startsWith("http") ? endpoint : `${API_BASE}${endpoint}`, baseUrl);
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined) url.searchParams.append(key, String(value));
    });
  }
  // 2. Prepare Headers (Auth + JSON)
  const headers = new Headers(fetchOptions.headers);
  if (!headers.has("Content-Type") && !(fetchOptions.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }
  const token = typeof window !== "undefined" ? localStorage.getItem(TOKEN_STORAGE_KEY) : null;
  if (token && !headers.has("Authorization")) {
    headers.set("Authorization", `Bearer ${token}`);
  }
  // 3. Execute with Retry Logic
  let lastError: any;
  for (let attempt = 0; attempt <= retries; attempt++) {
    try {
      if (typeof fetch !== "function") {
        throw new Error("Global 'fetch' is not a function. This may be due to a misconfigured environment or shadowing.");
      }
      const response = await fetch(url.toString(), {
        ...fetchOptions,
        headers,
      });
      // Handle successful status
      if (response.ok) {
        return (await response.json()) as T;
      }
      // Handle non-retryable errors (4xx)
      if (response.status >= 400 && response.status < 500) {
        if (response.status === 401 && !isOnAuthPage()) {
          handleUnauthorized();
        }
        const errorData = await response.json().catch(() => ({}));
        throw new APIError(response.status, errorData.message || response.statusText, errorData);
      }
      // Retryable errors (5xx)
      throw new APIError(response.status, `Server error: ${response.statusText}`);
    } catch (error) {
      lastError = error;

      // Don't retry if it's a 4xx error or we've exhausted attempts
      if (error instanceof APIError && error.status < 500) throw error;
      if (attempt === retries) break;
      // Exponential backoff
      const waitTime = backoff * Math.pow(2, attempt);
      console.warn(`API Request failed (${endpoint}). Retrying in ${waitTime}ms...`, error);
      await delay(waitTime);
    }
  }
  throw lastError || new Error(`Failed to fetch ${endpoint} after ${retries} retries`);
}

/**
 * Convenience methods for common HTTP verbs
 */
export const api = {
  get: <T>(url: string, params?: Record<string, any>, options?: RequestOptions) =>
    apiClient<T>(url, { ...options, method: "GET", params }),

  post: <T>(url: string, body: any, options?: RequestOptions) =>
    apiClient<T>(url, { ...options, method: "POST", body: JSON.stringify(body) }),

  put: <T>(url: string, body: any, options?: RequestOptions) =>
    apiClient<T>(url, { ...options, method: "PUT", body: JSON.stringify(body) }),

  patch: <T>(url: string, body: any, options?: RequestOptions) =>
    apiClient<T>(url, { ...options, method: "PATCH", body: JSON.stringify(body) }),

  delete: <T>(url: string, options?: RequestOptions) =>
    apiClient<T>(url, { ...options, method: "DELETE" }),
};
