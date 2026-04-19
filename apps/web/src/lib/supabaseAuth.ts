import { getAnonBrowserClient, getAuthenticatedSupabaseClient } from "./supabase/browserSingleton";
import { TOKEN_STORAGE_KEY } from "./authStorage";

/**
 * Shared anon client — same instance as `@/lib/supabase` (single GoTrue client).
 */
export const supabase = getAnonBrowserClient();

/**
 * Retrieves the current user's session token from localStorage.
 */
export const getSessionToken = (): string | null => {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(TOKEN_STORAGE_KEY) || localStorage.getItem("accessToken");
};

/**
 * Supabase client with the user's JWT. Memoized per token string.
 */
export const getAuthenticatedClient = (customToken?: string) => {
  const token = customToken || getSessionToken();

  if (!token) {
    return getAnonBrowserClient();
  }

  return getAuthenticatedSupabaseClient(token);
};
