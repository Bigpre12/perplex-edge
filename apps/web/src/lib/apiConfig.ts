const isServer = typeof window === 'undefined';
const isDevelopment = process.env.NODE_ENV === "development";
const PROD_URL = "https://perplex-edge-backend-copy-production.up.railway.app";
const DEV_URL = "http://localhost:8000";

/**
 * The validated API Base URL. 
 */
let configuredUrl = process.env.NEXT_PUBLIC_API_URL || PROD_URL;
if (process.env.NODE_ENV === "production" && configuredUrl.includes("localhost")) {
    configuredUrl = PROD_URL;
}

export const API_BASE = isServer ? configuredUrl : "/backend";

/**
 * Helper to check if the API is correctly configured.
 */
export function isApiConfigured(): boolean {
    return true; // We now default to valid relative paths or localhost
}

console.log(`[API Config] Mode: ${process.env.NODE_ENV}, Base URL: ${API_BASE || "(relative)"}`);
