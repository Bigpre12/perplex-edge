// sw.js — LUCRIX Service Worker v2
const CACHE_NAME = "lucrix-cache-v2";

// ── Install ──────────────────────────────────────────────
self.addEventListener("install", (event) => {
    console.log("[SW] Installing...");
    self.skipWaiting();
});

// ── Activate ─────────────────────────────────────────────
self.addEventListener("activate", (event) => {
    console.log("[SW] Activating...");
    event.waitUntil(
        caches.keys().then((keys) =>
            Promise.all(
                keys
                    .filter((key) => key !== CACHE_NAME)
                    .map((key) => caches.delete(key))
            )
        )
    );
    self.clients.claim();
});

// ── Fetch ─────────────────────────────────────────────────
self.addEventListener("fetch", (event) => {
    const { request } = event;
    const url = new URL(request.url);

    // ✅ NEVER intercept — pass straight through to network
    const skipPatterns = [
        url.port === "8000",                          // FastAPI backend
        url.pathname.startsWith("/api/"),             // API routes
        url.pathname.startsWith("/_next/"),           // Next.js internals
        url.pathname.includes("hot-update"),          // HMR
        url.pathname.includes("webpack"),             // Webpack
        url.hostname !== self.location.hostname,      // External URLs (ESPN, Odds API)
        request.method !== "GET",                     // POST/PUT/DELETE
    ];

    if (skipPatterns.some(Boolean)) {
        // Pass through — do NOT intercept. Let browser handle it natively.
        // This prevents "Failed to convert value to 'Response'" errors when SW fetch fails.
        return;
    }

    // For static assets only — cache then network
    event.respondWith(
        (async () => {
            const cache = await caches.open(CACHE_NAME);
            const cached = await cache.match(request);
            if (cached) return cached;

            try {
                const response = await fetch(request);
                // Only cache valid same-origin responses
                if (
                    response &&
                    response.status === 200 &&
                    response.type === "basic"
                ) {
                    cache.put(request, response.clone());
                }
                return response;
            } catch (err) {
                console.warn("[SW] Fetch failed:", request.url, err);
                // Return a valid empty response — never reject or return undefined
                return new Response("Network error - Service Unavailable", {
                    status: 503,
                    statusText: "Service Unavailable",
                    headers: { "Content-Type": "text/plain" },
                });
            }
        })()
    );
});
