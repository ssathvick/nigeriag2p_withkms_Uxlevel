import {landingService} from './dashboard-navigation';
// Run before deferred application bundles. Keep OAuth callback parameters intact;
// SPAs may only expose their default landing route after processing the callback.
(()=>{if(window.top!==window.self)return;const initial=new URL(location.href);
 const intentional=initial.searchParams.has('_nsipa_records')||initial.searchParams.has('demo')||initial.hash&&!/code=|state=|session_state=/.test(initial.hash);
 if(intentional)return;
 const authPage=/\/login\/?$|\/signin\/?$|\/callback\/?$/.test(initial.pathname);
 function redirect(){const service=landingService(location.href,authPage?initial.href:document.referrer);if(service){location.replace('https://nigeriag2p.com/registration/analytics?service='+encodeURIComponent(service));return true}return false}
 if(redirect())return;
 if(authPage||/code=|state=|session_state=/.test(initial.search+initial.hash)){
  const timer=setInterval(()=>{if(redirect())clearInterval(timer)},500);
  setTimeout(()=>clearInterval(timer),600000);
 }
})();
