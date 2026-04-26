// Mock Service Worker handlers for local dev
self.addEventListener('fetch', event => {
  // Example: intercept /api/ calls
  if (event.request.url.includes('/api/')) {
    event.respondWith(new Response(JSON.stringify({ ok: true }), { headers: { 'Content-Type': 'application/json' } }));
  }
});
