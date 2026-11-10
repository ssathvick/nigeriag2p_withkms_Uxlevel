'use strict';
const CACHE='ng2p-fictional-field-v2', SHELL='/registration/phase1/field';
const ASSETS=[SHELL,'/registration/static/phase1-field.js','/registration/static/style.css'];
self.addEventListener('install',event=>event.waitUntil(self.skipWaiting()));
self.addEventListener('activate',event=>event.waitUntil(self.clients.claim()));
self.addEventListener('message',event=>{if(event.data&&event.data.type==='CACHE_SHELL')event.waitUntil((async()=>{const cache=await caches.open(CACHE);for(const url of ASSETS){const response=await fetch(url+'?v=2',{credentials:'same-origin',cache:'no-store'});if(!response.ok||response.redirected)throw new Error('Shell unavailable');await cache.put(url,response);}if(event.source)event.source.postMessage({type:'OFFLINE_READY'});})());});
self.addEventListener('fetch',event=>{const url=new URL(event.request.url);if(event.request.method!=='GET'||url.origin!==self.location.origin||!ASSETS.includes(url.pathname))return;event.respondWith((async()=>{try{return await fetch(event.request);}catch(e){const cached=await caches.match(url.pathname,{cacheName:CACHE});if(cached)return cached;throw e;}})());});
