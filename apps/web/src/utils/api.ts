/**
 * API Utility helpers
 */

/**
 * Safe fetch wrapper to prevent SyntaxErrors when API returns non-JSON (like 500 errors)
 */
export async function safeFetch<T>(url: string, fallback: T): Promise<T> {
    try {
        const res = await fetch(url);
        if (!res.ok) {
            console.warn(`API ${url} returned ${res.status}`);
            return fallback;
        }
        const contentType = res.headers.get("content-type");
        if (contentType && contentType.includes("application/json")) {
            return await res.json();
        }
        return fallback;
    } catch (e) {
        console.warn(`API ${url} failed:`, e);
        return fallback;
    }
}
