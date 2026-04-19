import { getAnonBrowserClient } from "./supabase/browserSingleton";

export { getAnonBrowserClient } from "./supabase/browserSingleton";

if (!process.env.NEXT_PUBLIC_SUPABASE_URL || !process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY) {
  console.warn("Supabase env variables are missing. Direct DB queries will fail.");
}

export const supabase = getAnonBrowserClient();
