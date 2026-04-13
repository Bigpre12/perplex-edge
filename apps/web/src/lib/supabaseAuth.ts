import { createClient } from '@supabase/supabase-js';
import { TOKEN_STORAGE_KEY } from './authStorage';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || '';
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || '';

/**
 * Creates a standard unauthenticated client (or with the public anon key only).
 * Deprecated for data queries due to RLS policies.
 */
export const supabase = createClient(supabaseUrl, supabaseAnonKey);

/**
 * Retrieves the current user's session token from localStorage.
 */
export const getSessionToken = (): string | null => {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem(TOKEN_STORAGE_KEY) || localStorage.getItem("accessToken");
};

/**
 * Creates a dynamically authenticated Supabase client using the current user's JWT.
 * Assumes the FastAPI backend signs the JWT using the same JWT_SECRET configured in Supabase.
 * If no token is provided, uses the currently stored session token.
 */
export const getAuthenticatedClient = (customToken?: string) => {
    const token = customToken || getSessionToken();
    
    if (!token) {
        // Return anon client if no token found (most actions will be blocked by RLS)
        return supabase;
    }

    return createClient(supabaseUrl, supabaseAnonKey, {
        global: {
            headers: {
                Authorization: `Bearer ${token}`
            }
        }
    });
};
