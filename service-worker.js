const CACHE_NAME = "mathechecks-cache-v3"; // Version anpassen bei Änderungen
const urlsToCache = [
  "/",
  "/index.html",
  "/manifest.json",
  "/icons/icon-192.png",
  "/icons/icon-512.png",
  // "/offline.html" // optional, falls du eine Offline-Seite verwenden möchtest
];

// Installations-Event: Ressourcen cachen
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

// Fetch-Event: zuerst Cache, sonst Netzwerk (Fallback möglich)
self.addEventListener("fetch", (event) => {
  event.respondWith(
    caches.match(event.request).then((response) => {
      // Falls im Cache gefunden, zurückgeben; sonst vom Netz holen
      return (
        response ||
        fetch(event.request).catch(() => {
          // Optional: fallback bei Offline (z. B. "/offline.html")
          return caches.match("/offline.html");
        })
      );
    })
  );
});
