const CACHE_NAME = "mathechecks-cache-v17"; // Version hochsetzen!
const urlsToCache = [
  "/",
  "/manifest.json",
  "/icons/icon-192.png",
  "/icons/icon-512.png",
  // "/offline.html" // optional, falls Offline-Seite vorhanden
];

// Installations-Event: Basisressourcen cachen
self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(urlsToCache);
    })
  );
});

// Aktivierungs-Event: alte Caches löschen
self.addEventListener("activate", (event) => {
  const cacheWhitelist = [CACHE_NAME];
  event.waitUntil(
    caches.keys().then((cacheNames) =>
      Promise.all(
        cacheNames.map((cacheName) => {
          if (!cacheWhitelist.includes(cacheName)) {
            return caches.delete(cacheName);
          }
        })
      )
    )
  );
});

// Fetch-Event: Strategie je nach Dateityp
self.addEventListener("fetch", (event) => {
  const request = event.request;

  // 1. HTML-Seiten (Navigation) -> Network first
  if (request.mode === "navigate") {
    event.respondWith(
      fetch(request)
        .then((response) => {
          // Aktuelle Version auch in den Cache legen, aber nur bei GET
          if (request.method === "GET") {
            const clone = response.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(request, clone));
          }
          return response;
        })
        .catch(() =>
          caches
            .match(request)
            .then((res) => res || caches.match("/offline.html"))
        )
    );
    return;
  }

  // 2. Statische Dateien (Icons, Manifest, CSS/JS) -> Cache first
  event.respondWith(
    caches.match(request).then((response) => {
      return (
        response ||
        fetch(request).then((res) => {
          if (request.method === "GET") {
            const clone = res.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(request, clone));
          }
          return res;
        })
      );
    })
  );
});
