const {chromium}=require('playwright'),fs=require('fs'),assert=require('assert/strict');
const out='H:/Nigeria_Mosip/codex/output/auth-recovery-verification';fs.mkdirSync(out,{recursive:true});
const credentials=JSON.parse(fs.readFileSync('H:/Nigeria_Mosip/Credentials/mbr_demo_credentials.json','utf8'));
(async()=>{const browser=await chromium.launch({channel:'msedge',headless:true}),results=[];try{
for(const host of ['g2p-register.wverve.in','register.nigeriag2p.com']){
for(const scenario of ['unauthorized-code','unauthorized-empty','service-retry','forbidden']){
 const context=await browser.newContext({ignoreHTTPSErrors:true,viewport:{width:390,height:844}}),page=await context.newPage();let calls=0;
 await page.route('**/api/me',route=>{calls++;const status=scenario.startsWith('unauthorized')?401:scenario==='forbidden'?403:503;return route.fulfill({status,contentType:scenario==='unauthorized-empty'?'text/plain':'application/json',body:scenario==='unauthorized-empty'?'Unauthorized':JSON.stringify({errors:[{code:'G2P-AUT-401',message:'Unauthorized'}]})})});
 await page.goto('https://'+host+'/en');
 if(scenario.startsWith('unauthorized')){await page.locator('#username').waitFor({timeout:30000});assert(!/Something went wrong/.test(await page.locator('body').innerText()));}
 else if(scenario==='service-retry'){await page.getByRole('button',{name:'Try again',exact:true}).click();await page.getByRole('button',{name:'Try again',exact:true}).waitFor();assert(calls>=2);}
 else await page.getByRole('heading',{name:/Access denied/i}).waitFor();
 assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+3));results.push({host,scenario,status:'passed'});await context.close();
}
for(const email of ['abuchi@gmail.com','aarin@gmail.com','abutu@gmail.com','adaku@gmail.com','admin@openg2p.org']){
 const context=await browser.newContext({ignoreHTTPSErrors:true}),page=await context.newPage();await page.goto('https://'+host+'/en');await page.locator('#username').fill(email);await page.locator('#password').fill(credentials[email].password);await page.locator('form').filter({has:page.locator('#password')}).locator('[type=submit]').click();await page.waitForURL('**/en**');await page.getByRole('heading',{name:/^Registry overview/}).waitFor({timeout:30000});
 results.push({host,role:email,status:'passed',dashboard:true});await context.close();
}
}
fs.writeFileSync(out+'/results.json',JSON.stringify({status:'passed',results},null,2));console.log('PASS '+results.length+' authentication recovery and role login checks');
}finally{await browser.close()}})().catch(e=>{console.error(e.message);process.exitCode=1});
