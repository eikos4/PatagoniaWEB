/* Service Worker — Admin (Patagonia Export) */
const CACHE = 'ps-admin-v1';
const PRECACHE = [
  '/static/css/ps-loading.css',
  '/static/js/ps-loading.js',
  '/static/img/pwa/ship-admin-192.png',
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE).then((cache) => cache.addAll(PRECACHE)).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  if (event.request.method !== 'GET') return;
  const url = new URL(event.request.url);
  if (!url.pathname.startsWith('/admin') && !url.pathname.startsWith('/static')) return;

  event.respondWith(
    fetch(event.request)
      .then((res) => {
        if (res.ok && url.pathname.startsWith('/static')) {
          const copy = res.clone();
          caches.open(CACHE).then((cache) => cache.put(event.request, copy));
        }
        return res;
      })
      .catch(() => caches.match(event.request))
  );
});
