// Minimal service worker placeholder to avoid 404s
self.addEventListener('install', (event) => {
  self.skipWaiting();
});
self.addEventListener('activate', (event) => {
  event.waitUntil(self.clients.claim());
});
// No fetch handler — let the browser use network by default and avoid no-op handler warnings.
