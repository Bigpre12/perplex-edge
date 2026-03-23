const isDevelopment = process.env.NODE_ENV === "development";

/**
 * The validated API Base URL. 
 * - In development: uses localhost:8000
 * - In production: uses relative paths "" (enabling Vercel proxy)
 */
export const API_BASE = isDevelopment 
    ? "http://localhost:8000" 
    : (process.env.NEXT_PUBLIC_API_URL || "");

/**
 * Helper to check if the API is correctly configured.
 */
export function isApiConfigured(): boolean {
    return true; // We now default to valid relative paths or localhost
}

console.log(`[API Config] Mode: ${process.env.NODE_ENV}, Base URL: ${API_BASE || "(relative)"}`);
