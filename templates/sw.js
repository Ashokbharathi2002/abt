const CACHE_NAME = 'ab-traders-cache-v1';
const ASSETS = [
  '/',
  '/static/css/style.css',
  '/static/images/icons/icon-192x192.png',
  '/static/images/icons/icon-512x512.png',
  'https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css',
  'https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap'
];

// Install Event (Robust, fail-safe caching)
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log('[Service Worker] Caching files individually');
      return Promise.allSettled(
        ASSETS.map((asset) => {
          return fetch(asset)
            .then((response) => {
              if (response.ok) {
                return cache.put(asset, response);
              }
              throw new Error(`Failed to fetch ${asset} (Status: ${response.status})`);
            })
            .catch((err) => {
              console.warn(`[Service Worker] Skipping cache for asset ${asset}:`, err);
            });
        })
      );
    })
  );
});

// Activate Event
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.map((key) => {
          if (key !== CACHE_NAME) {
            console.log('[Service Worker] Removing old cache', key);
            return caches.delete(key);
          }
        })
      );
    })
  );
});

// Fetch Event (Network first, fallback to Cache)
self.addEventListener('fetch', (event) => {
  if (event.request.method !== 'GET') return;

  event.respondWith(
    fetch(event.request)
      .then((networkResponse) => {
        if (networkResponse.status === 200) {
          const cacheCopy = networkResponse.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(event.request, cacheCopy);
          });
        }
        return networkResponse;
      })
      .catch(() => {
        return caches.match(event.request).then((cachedResponse) => {
          if (cachedResponse) {
            return cachedResponse;
          }
        });
      })
  );
});
