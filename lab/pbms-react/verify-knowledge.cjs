const {chromium}=require('playwright');
const {execFileSync}=require('node:child_process');
const fs=require('node:fs');const assert=require('node:assert/strict');
const plan=JSON.parse(fs.readFileSync('../knowledge/guidance-corrections.json','utf8'));
const resolve=require('../knowledge/context.js').resolve;
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'msedge'});const results=[];
 try{
 for(const host of ['pbms.nigeriag2p.com','g2p-pbms.wverve.in']){
  const context=await browser.newContext({viewport:{width:1440,height:1000}});const page=await context.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto('https://'+host+'/');await page.locator('#ng-km-launcher').click();await page.locator('#ng-km-panel h3').waitFor();
  assert.equal(await page.locator('#ng-km-panel h3').first().innerText(),'Sign in');await page.locator('.ng-km-close').click();
  const cookies=JSON.parse(execFileSync('wsl',['-d','Ubuntu-22.04','-u','root','--','python3','/mnt/h/Nigeria_Mosip/codex/openg2p-lab/pbms-react/verify-api.py','--browser-session','--host',host],{encoding:'utf8',stdio:['ignore','pipe','pipe']}));await context.addCookies(cookies);await page.reload();await page.locator('.sidebar nav a').first().waitFor();
  const links=await page.locator('.sidebar nav a').evaluateAll(es=>es.map(e=>({hash:e.getAttribute('href'),label:e.textContent.slice(1)})));
  assert.equal(links.length,21);for(const link of links){
   await page.locator('.sidebar nav a[href="'+link.hash+'"]').click();await page.locator('.table-wrap[aria-busy="false"]').waitFor();
   await page.locator('#ng-km-launcher').click();
   const expected=plan.new.find(a=>a.stage===link.label);assert(expected,link.label);
   await page.waitForFunction(t=>document.querySelector('#ng-km-panel h3')?.textContent===t,expected.title);
   const content=await page.locator('#ng-km-panel').innerText();assert(content.includes(expected.purpose));for(const step of expected.steps.split('\n'))assert(content.includes(step));
   assert(!/Nigeria[\s-]*G2P\b(?!\.)/i.test(await page.locator('body').innerText()));
   await page.locator('.ng-km-close').click();results.push(host+link.hash);
  }
  await page.getByRole('button',{name:'Open →',exact:true}).first().click();
  await page.getByRole('button',{name:'Verification',exact:true}).click();await page.locator('#ng-km-launcher').click();
  await page.waitForFunction(()=>document.querySelector('#ng-km-panel h3')?.textContent==='Verification queue');await page.locator('.ng-km-close').click();
  await page.getByRole('button',{name:'Payments',exact:true}).click();await page.locator('#ng-km-launcher').click();
  await page.waitForFunction(()=>document.querySelector('#ng-km-panel h3')?.textContent==='Payments');await page.locator('.ng-km-close').click();await page.getByRole('button',{name:'Close workflow',exact:true}).click();
  await page.setViewportSize({width:390,height:844});await page.locator('#ng-km-launcher').click();await page.locator('#ng-km-panel h3').waitFor();
  // Reproduce hostile host-card typography: help must still display complete sentences.
  await page.route('**/iqs-brand/hostile-test.css',route=>route.fulfill({contentType:'text/css',body:'p,li{white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-height:20px;-webkit-line-clamp:1}'}));await page.addStyleTag({url:'/iqs-brand/hostile-test.css'});
  const clipped=await page.locator('#ng-km-panel p,#ng-km-panel li').evaluateAll(es=>es.filter(e=>{const c=getComputedStyle(e);return c.whiteSpace==='nowrap'||c.overflow==='hidden'||c.webkitLineClamp==='1'||e.scrollWidth>e.clientWidth+2;}).map(e=>e.textContent));assert.deepEqual(clipped,[]);
  await page.locator('.ng-km-content').evaluate(e=>e.scrollTop=e.scrollHeight);await page.screenshot({path:'evidence/knowledge-'+host+'.png'});
  assert.deepEqual(errors,[]);await context.close();
 }
 for(const host of ['nigeriag2p.com','g2p.wverve.in']){
  const context=await browser.newContext();const page=await context.newPage();await page.goto('https://'+host+'/registration/knowledge');if(new URL(page.url()).hostname!==host)await page.goto('https://'+host+'/');
  await page.locator('#ng-km-launcher').click();await page.locator('#ng-km-panel h3').waitFor();
  const payload=await page.evaluate(async()=>await(await fetch('/iqs-brand/knowledge?audience=all&include_roles=1')).json());
  assert.equal(payload.articles.length,require('../knowledge-seed.json').articles.length);for(const a of payload.articles){for(const field of ['purpose','steps','requirements','next_step','issues'])assert(a[field]?.trim(),`${a.id} ${field}`);assert(!/Nigeria[\s-]*G2P\b(?!\.)/i.test(JSON.stringify(a)));}
  assert(!/Nigeria[\s-]*G2P\b(?!\.)/i.test(await page.locator('body').innerText()));results.push(host+' library: '+payload.articles.length+' articles');await context.close();
 }
 for(const service of ['register','registry','beneficiary','pbms','awe','portal-admin','odk','superset','master-data-ui','partner-management','consent-manager','staff-portal','iam-staff-ui']){
  const first=resolve({hostname:service+'.nigeriag2p.com'});const second=resolve({hostname:'g2p-'+service+'.wverve.in'});assert.equal(first.module,second.module);assert.equal(first.stage,second.stage);
 }
 fs.writeFileSync('evidence/knowledge-verification.json',JSON.stringify({passed:results,domainMappings:26},null,2));console.log(JSON.stringify({passed:results.length,domainMappings:26}));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1});
