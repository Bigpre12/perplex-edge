// sw.js — LUCRIX Service Worker v4 (bust caches; never intercept App Router RSC fetches)
const CACHE_NAME = "lucrix-cache-v4";

// ── Install ──────────────────────────────────────────────
self.addEventListener("install", (event) => {
    console.log("[SW] Installing v4...");
    self.skipWaiting();
});

// ── Activate ─────────────────────────────────────────────
self.addEventListener("activate", (event) => {
    console.log("[SW] Activating v4...");
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

    // 1. Navigation requests (HTML pages) should ALWAYS be Network-First.
    // This prevents stale index.html from pointing to deleted _next chunks.
    if (request.mode === 'navigate') {
        event.respondWith(
            fetch(request).catch(async () => {
                const cache = await caches.open(CACHE_NAME);
                const cachedResponse = await cache.match(request);
                return cachedResponse || new Response("Offline - Content Unavailable", {
                    status: 503,
                    statusText: "Service Unavailable",
                    headers: { "Content-Type": "text/html" }
                });
            })
        );
        return;
    }

    // 2. ✅ NEVER intercept — pass straight through to network
    // Next.js App Router: RSC / flight requests are same-origin GETs to route URLs (not /_next/).
    // Cache-first on those serves stale flight data across deploys and breaks chunk loading.
    const h = request.headers;
    const isNextDataFlight =
        h.get("RSC") === "1" ||
        h.has("Next-Router-State-Tree") ||
        h.get("Next-Router-Prefetch") === "1" ||
        h.has("Next-Action");

    const skipPatterns = [
        isNextDataFlight,
        url.port === "8000",                          // FastAPI backend
        url.pathname.startsWith("/api/"),             // API routes
        url.pathname.startsWith("/_next/"),           // Next.js internals (already hashed)
        url.pathname.includes("hot-update"),          // HMR
        url.pathname.includes("webpack"),             // Webpack
        url.hostname !== self.location.hostname,      // External URLs
        request.method !== "GET",                     // POST/PUT/DELETE
    ];

    if (skipPatterns.some(Boolean)) {
        return;
    }

    // 3. For static assets (images, fonts) — Cache First with Network Fallback
    event.respondWith(
        (async () => {
            const cache = await caches.open(CACHE_NAME);
            const cached = await cache.match(request);
            if (cached) return cached;

            try {
                const response = await fetch(request);
                // Only cache valid same-origin GET responses
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
                return new Response("Network error", { status: 408 });
            }
        })()
    );
});

