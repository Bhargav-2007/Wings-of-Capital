const CACHE_NAME = 'woc-v1';
const ASSETS = [
  '/',
  '/index.html',
  '/dashboard.html',
  '/css/design-system.css',
  '/css/styles.css',
  '/css/components.css',
  '/css/utilities.css',
  '/css/dashboard.css',
  '/js/theme.js',
  '/js/state.js',
  '/js/api.js',
  '/js/auth.js',
  '/js/components/sidebar.js',
  '/js/components/charts.js',
  '/js/utils/formatters.js'
];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE_NAME).then(c => c.addAll(ASSETS)));
});

self.addEventListener('fetch', e => {
  e.respondWith(caches.match(e.request).then(res => res || fetch(e.request)));
});
