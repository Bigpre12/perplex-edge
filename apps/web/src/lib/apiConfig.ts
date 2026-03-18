/**
 * Runtime API Configuration Validation
 * Ensures that the frontend doesn't silently fail due to missing environment variables.
 */

const rawApiUrl = process.env.NEXT_PUBLIC_API_URL || "";

// Check for missing or placeholder values
const isPlaceholder = rawApiUrl.includes("<your-cloud-run-domain>") || rawApiUrl === "REPLACE_WITH_ACTUAL_BACKEND_URL";
const isMissing = !rawApiUrl;

if (typeof window !== "undefined") {
    if (isMissing) {
        console.error(
            "CRITICAL: NEXT_PUBLIC_API_URL is missing! Every API call will fallback to localhost:8000. " +
            "Please set this in Vercel Dashboard -> Settings -> Environment Variables."
        );
    } else if (isPlaceholder) {
        console.error(
            "CRITICAL: NEXT_PUBLIC_API_URL still contains a placeholder value! " +
            "Please update this in Vercel Dashboard with your actual backend URL."
        );
    }
}

/**
 * The validated API host URL (no trailing slash).
 * Falls back to localhost:8000 during development if no env var is set.
 */
export const API_HOST = !isMissing && !isPlaceholder
    ? rawApiUrl.replace(/\/$/, "")
    : "http://localhost:8000";

/**
 * Browser requests should use same-origin `/api/*` so Next.js rewrites can proxy
 * to the backend without triggering browser CORS.
 *
 * Server-side requests (Node) need an absolute URL.
 */
export const API_BASE = typeof window !== "undefined" ? "" : API_HOST;

/**
 * Helper to check if the production API is correctly configured.
 */
export function isApiConfigured(): boolean {
    return !isMissing && !isPlaceholder;
}

console.log(`[API Config] Base URL: ${API_BASE}`);
