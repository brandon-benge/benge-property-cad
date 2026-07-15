const CACHE_PREFIX = "python-cad-viewer";
const CACHE_NAME = `${CACHE_PREFIX}-v1`;

self.addEventListener("install", (event) => {
  event.waitUntil(caches.open(CACHE_NAME).then((cache) => cache.addAll(["./", "./index.html"])));
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    Promise.all([
      caches
        .keys()
        .then((keys) => Promise.all(keys.filter((key) => key.startsWith(CACHE_PREFIX) && key !== CACHE_NAME).map((key) => caches.delete(key)))),
      self.clients.claim(),
    ]),
  );
});

self.addEventListener("message", (event) => {
  if (event.data?.type !== "CACHE_MODEL") return;
  event.waitUntil(
    fetch("./model/download-manifest.json")
      .then((response) => response.json())
      .then(async (manifest) => {
        const cache = await caches.open(CACHE_NAME);
        const files = (manifest.files || []).map((file) => `./model/${file.path}`);
        await Promise.allSettled(["./model/download-manifest.json", ...files].map((url) => cache.add(url)));
      }),
  );
});

self.addEventListener("fetch", (event) => {
  if (event.request.method !== "GET") return;
  event.respondWith(
    caches.match(event.request).then((cached) => {
      if (cached) return cached;
      return fetch(event.request).then((response) => {
        if (!response.ok || response.type === "opaque") return response;
        const copy = response.clone();
        caches.open(CACHE_NAME).then((cache) => cache.put(event.request, copy));
        return response;
      });
    }),
  );
});
