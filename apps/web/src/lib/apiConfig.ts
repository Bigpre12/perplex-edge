const isServer = typeof window === 'undefined';
const isDevelopment = process.env.NODE_ENV === "development";
const PROD_URL = "https://perplex-edge-backend-production.up.railway.app";
const DEV_URL = "http://localhost:8000";

/**
 * The validated API Base URL. 
 */
export const API_BASE = isServer 
    ? (process.env.NEXT_PUBLIC_API_URL || (isDevelopment ? DEV_URL : PROD_URL))
    : ""; // Use relative paths in the browser to avoid CORS (proxying through Next.js)

/**
 * Helper to check if the API is correctly configured.
 */
export function isApiConfigured(): boolean {
    return true; // We now default to valid relative paths or localhost
}

console.log(`[API Config] Mode: ${process.env.NODE_ENV}, Base URL: ${API_BASE || "(relative)"}`);
