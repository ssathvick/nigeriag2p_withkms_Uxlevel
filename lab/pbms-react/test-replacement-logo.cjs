const {chromium}=require('playwright');const {execFileSync}=require('child_process');const fs=require('fs');const assert=require('assert/strict');
const out='H:/Nigeria_Mosip/codex/output/logo-replacement';fs.mkdirSync(out,{recursive:true});
const creds=JSON.parse(execFileSync('wsl',['-d','Ubuntu-22.04','-u','root','--','cat','/opt/openg2p-lab/registration/mbr-demo-credentials.json'],{encoding:'utf8',stdio:['ignore','pipe','pipe']}));
(async()=>{const browser=await chromium.launch({channel:'msedge',headless:true});let page;const checks=[];const errors=[];try{
 const context=await browser.newContext({viewport:{width:1440,height:1050},ignoreHTTPSErrors:true});page=await context.newPage();page.on('pageerror',e=>errors.push(e.message));
 async function logo(selector,name){await page.locator(selector).first().waitFor();await page.waitForFunction(selector=>{const img=document.querySelector(selector);return img&&img.complete&&img.naturalWidth>0},selector);const box=await page.locator(selector).first().boundingBox();assert(box.width>30&&box.height>25);checks.push(name);await page.screenshot({path:out+'/'+name+'.png',fullPage:false})}
 await page.goto('https://g2p.wverve.in/');await logo('.hub-brand img','service-hub');
 await page.goto('https://g2p.wverve.in/registration/mbr');await page.locator('#username').waitFor();await page.locator('.iqs-logo-mark').waitFor();assert((await page.locator('.iqs-logo-mark').first().evaluate(el=>getComputedStyle(el).backgroundImage)).includes('nsipa-logo'));checks.push('staff-sign-in');await page.screenshot({path:out+'/staff-sign-in.png'});
 await page.locator('#username').fill('aarin@gmail.com');await page.locator('#password').fill(creds['aarin@gmail.com'].password);await page.locator('input[type=submit],button[type=submit]').first().click();await logo('.mbr-top img.mbr-logo','registry-desktop');assert.equal(await page.locator('.mbr-top .mbr-logo').innerText(),'');
 await page.setViewportSize({width:390,height:844});assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));await logo('.mbr-top img.mbr-logo','registry-mobile');await page.setViewportSize({width:1440,height:1050});
 await page.goto('https://g2p-pbms.wverve.in/pbms-ui/');await logo('.brand img.nsipa-product-logo','pbms-sign-in');
 await page.goto('https://g2p.wverve.in/registration/workspace');await logo('.wordmark img','staff-workspace');
 for(const [url,name] of [['https://g2p.wverve.in/territories/','territorial-atlas'],['https://g2p.wverve.in/jos-cct/','jos-pilot']]){await page.goto(url);await logo('header img[src*="nsipa"]',name)}
 fs.writeFileSync(out+'/browser-verification.json',JSON.stringify({status:'passed',checks,consoleErrors:errors},null,2));console.log(JSON.stringify({status:'passed',checks,consoleErrors:errors}));
 }catch(e){if(page)await page.screenshot({path:out+'/failure.png'});throw e}finally{await browser.close()}})().catch(e=>{console.error(e.message);process.exitCode=1});
