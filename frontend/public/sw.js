// public/sw.js - Lucrix Service Worker
const CACHE_NAME = 'perplex-edge-v5'; // Bumped cache to forcibly purge old HTML static chunks
const STATIC_ASSETS = ['/', '/arbitrage', '/player-props', '/ledger'];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(STATIC_ASSETS))
  );
  self.skipWaiting();
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
    )
  );
  self.clients.claim();
});

self.addEventListener('fetch', event => {
  // 1. Immediately bypass all non-GET requests (POST, PUT, DELETE, OPTIONS, etc.)
  if (event.request.method !== 'GET') {
    return;
  }

  const url = new URL(event.request.url);

  // 2. Bypass all cross-origin requests (e.g., our FastAPI backend running on port 8000)
  if (url.origin !== self.location.origin) {
    return;
  }

  // 3. Bypass explicit backend proxy routes, Next.js HMR, and other non-cacheable data
  if (url.pathname.startsWith('/api/') || url.pathname.startsWith('/immediate/') || url.pathname.startsWith('/_next/')) {
    return;
  }

  // Handle same-origin static assets and GET requests
  event.respondWith(
    caches.match(event.request).then(cached => cached || fetch(event.request))
  );
});

self.addEventListener('push', event => {
  const data = event.data ? event.data.json() : {};
  event.waitUntil(
    self.registration.showNotification(data.title || '⚡ Sharp Pick Alert', {
      body: data.body || 'New high-value intelligence available',
      icon: '/icons/icon-192.png',
      badge: '/icons/icon-192.png',
      data: { url: data.url || '/player-props' },
      actions: [{ action: 'view', title: 'Open Dashboard' }]
    })
  );
});

self.addEventListener('notificationclick', event => {
  event.notification.close();
  event.waitUntil(clients.openWindow(event.notification.data.url || '/player-props'));
});
