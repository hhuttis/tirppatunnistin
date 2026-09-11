/* Tirppatunnistimen service worker.
   build.py tayttaa build-tunnisteen ja valimuistilistan joka julkaisussa.
   Tata tiedostoa ei tarvitse muokata kasin. */

const BUILD = '__BUILD__';
const CACHE = 'tirppatunnistin-' + BUILD;
const PRECACHE = __PRECACHE__;

// Sovellus lataa Reactin unpkg:stä ja linnun kuvat/äänet Wikimedia Commonsista.
// unpkg-tiedostot ovat versioituja eli ne saa tallentaa pysyvästi välimuistiin.
const VENDOR = /^https:\/\/unpkg\.com\//;

self.addEventListener('install', (e) => {
  e.waitUntil((async () => {
    const cache = await caches.open(CACHE);
    // Yksitellen, jotta yksi puuttuva tiedosto ei kaada koko asennusta.
    await Promise.all(PRECACHE.map((url) => cache.add(new Request(url, { cache: 'reload' })).catch(() => {})));
    self.skipWaiting();
  })());
});

self.addEventListener('activate', (e) => {
  e.waitUntil((async () => {
    const nimet = await caches.keys();
    await Promise.all(nimet.filter((n) => n.startsWith('tirppatunnistin-') && n !== CACHE).map((n) => caches.delete(n)));
    await self.clients.claim();
  })());
});

self.addEventListener('fetch', (e) => {
  const req = e.request;
  if (req.method !== 'GET') return;

  const url = new URL(req.url);
  const scope = new URL(self.registration.scope);
  const oma = url.origin === scope.origin && url.pathname.startsWith(scope.pathname);

  // Sivun avaus: verkko ensin, jotta uusi versio näkyy heti. Offline -> välimuisti.
  if (req.mode === 'navigate') {
    e.respondWith((async () => {
      try {
        const vastaus = await fetch(req);
        const cache = await caches.open(CACHE);
        cache.put(new Request(scope.pathname + 'index.html'), vastaus.clone());
        return vastaus;
      } catch (err) {
        const cache = await caches.open(CACHE);
        return (await cache.match(scope.pathname + 'index.html')) ||
               (await cache.match(scope.pathname)) ||
               Response.error();
      }
    })());
    return;
  }

  if (VENDOR.test(req.url)) {
    e.respondWith((async () => {
      const cache = await caches.open(CACHE);
      const osuma = await cache.match(req);
      if (osuma) return osuma;
      const vastaus = await fetch(req);
      if (vastaus && (vastaus.ok || vastaus.type === 'opaque')) cache.put(req, vastaus.clone());
      return vastaus;
    })());
    return;
  }

  if (oma) {
    // Omat tiedostot: välimuisti heti, päivitys taustalla.
    e.respondWith((async () => {
      const cache = await caches.open(CACHE);
      const osuma = await cache.match(req);
      const haku = fetch(req).then((vastaus) => {
        if (vastaus && vastaus.ok) cache.put(req, vastaus.clone());
        return vastaus;
      }).catch(() => null);
      return osuma || (await haku) || Response.error();
    })());
  }
  // Muut (Wikimedia Commons yms.) menevät suoraan verkkoon.
});
