const assert=require('node:assert/strict');
const esbuild=require('esbuild');
const Module=require('module');
const result=esbuild.buildSync({entryPoints:['src/dashboard-navigation.js'],bundle:true,platform:'node',format:'cjs',write:false});
const compiled=new Module('dashboard-navigation');compiled._compile(result.outputFiles[0].text,'dashboard-navigation.cjs');
const {landingService,landingPaths,origins,recordsUrl}=compiled.exports;
let checks=0;
for(const [service,paths] of Object.entries(landingPaths)){
 const origin='https://'+(origins[service]?'g2p-'+origins[service]+'.wverve.in':'g2p.wverve.in');
 for(const path of paths){
  const href=origin+path;
  assert.equal(landingService(href),service);checks++;
  for(const suffix of ['?_nsipa_records=1','?demo=1','?code=oauth&state=nonce','#action=193','?view=details','?state=Kano']){assert.equal(landingService(href+suffix),null);checks++}
  assert.equal(landingService(href,origin+'/web/login'),service);checks++;
  assert.equal(landingService(href,origin+'/records/123'),null);checks++;
 }
 const action=recordsUrl(service);
 assert.match(new URL(action).hostname,/^g2p(?:-[a-z0-9-]+)?\.wverve\.in$/,'Every service action must stay on the migrated domain');
 assert.equal(new URL(action).searchParams.get('_nsipa_records'),'1');
 assert.equal(landingService(action),null);checks+=2;
}
assert.equal(landingService('https://g2p.wverve.in/registration/analytics?service=pbms'),null);
assert.equal(landingService('https://g2p-keycloak.wverve.in/realms/staff/protocol/openid-connect/auth'),null);
assert.equal(new URL(recordsUrl('register','registry_records','Individual records')).searchParams.get('view'),'individuals');
assert.equal(new URL(recordsUrl('register','change_request_status')).searchParams.get('view'),'changes');
assert.match(recordsUrl('registry','registrant_inventory','Individuals'),/action=190/);
assert.match(recordsUrl('pbms','beneficiary_list_workflow'),/action=195/);
assert.match(recordsUrl('portal-admin','entitlement_lifecycle'),/action=399/);
assert.match(recordsUrl('consent-manager','consent_audit_inventory','Consent partners'),/\/partners/);
assert.match(recordsUrl('beneficiary','my_application_status','',true),/^https:\/\/g2p.wverve.in\/registration\//);
assert.match(recordsUrl('beneficiary','my_portal_memberships','',true),/g2p-beneficiary.wverve.in\/selfservice\/en\/applications/);
assert.ok(!recordsUrl('beneficiary','my_portal_memberships','',true).includes('portal-admin'));
assert.equal(landingService('https://g2p-pbms.wverve.in/web?db=pbmsdb'),'pbms');
console.log(`${checks+11} navigation checks passed: service defaults, deep links, callback exclusions, citizen scope, and native record routes.`);
const vm=require('node:vm');
const loader=esbuild.buildSync({entryPoints:['src/dashboard-landing.js'],bundle:true,write:false}).outputFiles[0].text;
function runLanding(href,referrer=''){
 const timers=[];const redirects=[];const frame={};const location={href,replace:u=>redirects.push(u)};
 vm.runInNewContext(loader,{URL,location,document:{referrer},window:{top:frame,self:frame},setInterval:fn=>{timers.push(fn);return 1},clearInterval:()=>{},setTimeout:()=>{}});
 return {timers,redirects,location};
}
// The established compatibility loader is deliberately a no-op: route ownership is now enforced at the server.
for(const href of ['https://g2p-pbms.wverve.in/web','https://g2p-pbms.wverve.in/web?_nsipa_records=1#action=195',
 'https://g2p-awe.wverve.in/#code=private&state=nonce','https://g2p-beneficiary.wverve.in/selfservice/en/login']){
 const scenario=runLanding(href);assert.equal(scenario.redirects.length,0);assert.equal(scenario.timers.length,0);
}
console.log('Compatibility loader checks passed: requested routes and OAuth destinations remain unchanged.');
