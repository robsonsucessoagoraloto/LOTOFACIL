// Service worker do app Lotofácil: guarda uma cópia para funcionar sem internet.
// Sempre tenta a internet primeiro (para pegar resultados novos) e usa a cópia só se estiver offline.
const CACHE = 'lotofacil-v1';
const BASE = ['./', './index.html', './resultados.json', './manifest.webmanifest',
  './icon-192.png', './icon-512.png', './icon-maskable-512.png', './apple-touch-icon.png', './favicon.png'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(BASE)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil(caches.keys()
    .then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});

self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;               // chamadas da API (POST) passam direto
  const url = new URL(req.url);
  const fonte = url.hostname === 'fonts.googleapis.com' || url.hostname === 'fonts.gstatic.com';
  if (url.origin !== self.location.origin && !fonte) return;

  if (fonte) {                                     // fontes: usa a cópia e atualiza em segundo plano
    e.respondWith(caches.open(CACHE).then(async c => {
      const hit = await c.match(req);
      const net = fetch(req).then(r => { if (r.ok || r.type === 'opaque') c.put(req, r.clone()); return r; }).catch(() => hit);
      return hit || net;
    }));
    return;
  }

  e.respondWith(fetch(req).then(r => {             // arquivos do app: internet primeiro
    if (r.ok) { const cp = r.clone(); caches.open(CACHE).then(c => c.put(req, cp)); }
    return r;
  }).catch(async () => {
    const c = await caches.open(CACHE);
    return (await c.match(req, {ignoreSearch: true})) ||
           (req.mode === 'navigate' ? await c.match('./index.html') : undefined) ||
           Response.error();
  }));
});
