import { createClient, SupabaseClient } from "@supabase/supabase-js";

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || "";
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || "";

let anonClient: SupabaseClient | null = null;

/** Single anon-key client per JS runtime (avoids multiple GoTrueClient warnings). */
export function getAnonBrowserClient(): SupabaseClient {
  if (!anonClient) {
    anonClient = createClient(supabaseUrl, supabaseAnonKey);
  }
  return anonClient;
}

let authedCache: { token: string; client: SupabaseClient } | null = null;

/** Reuse one client per JWT instead of creating a new Supabase client on every hook call. */
export function getAuthenticatedSupabaseClient(token: string): SupabaseClient {
  if (authedCache?.token === token) {
    return authedCache.client;
  }
  const client = createClient(supabaseUrl, supabaseAnonKey, {
    global: {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    },
  });
  authedCache = { token, client };
  return client;
}
