const {chromium}=require('playwright');
const fs=require('fs');const assert=require('assert/strict');
const credentials=JSON.parse(fs.readFileSync('H:/Nigeria_Mosip/Credentials/mbr_demo_credentials.json','utf8'));
const output='H:/Nigeria_Mosip/codex/output/native-registry-account-verification';fs.mkdirSync(output,{recursive:true});
(async()=>{
 const browser=await chromium.launch({channel:'msedge',headless:true});const results=[];
 try{for(const [email,config] of Object.entries(credentials)){
  const context=await browser.newContext({ignoreHTTPSErrors:true,viewport:{width:1440,height:1000}});const page=await context.newPage();
  await page.goto('https://g2p-register.wverve.in/en');
  for(let i=0;i<15;i++){
   await page.waitForTimeout(500);
   if(await page.locator('#username').count()){
    await page.locator('#username').fill(email);await page.locator('#password').fill(config.password);await page.locator('form').filter({has:page.locator('#password')}).locator('[type=submit]').click();
   }else if(new URL(page.url()).hostname==='g2p-register.wverve.in'&&!page.url().includes('callback')){
    const login=page.getByRole('button',{name:/log.?in|sign.?in/i});
    if(await login.count())await login.first().click();
    else if((await context.cookies()).some(c=>c.name==='X-Access-Token'))break;
   }
  }
  const cookies=await context.cookies();assert(cookies.some(c=>c.name==='X-Access-Token'),'Native sign-in cookie missing for '+email);
  const response=await context.request.get('https://g2p-register.wverve.in/api/permissions');assert.equal(response.status(),200);
  const data=await response.json();const permissions=data.flatMap(app=>app.permissions||[]);
  assert(permissions.includes('register:view'),'Master Registry inaccessible: '+email);
  const reviewer=['mbr-level1','mbr-level2'].includes(config.role);
  assert.equal(permissions.includes('intakeSubmission:approve'),reviewer,'Approval permission mismatch: '+email);
  assert.equal(permissions.includes('intakeSubmission:edit'),['mbr-officer','mbr-field-agent'].includes(config.role),'Capture permission mismatch: '+email);
  const taskStats=await context.request.get('https://g2p-register.wverve.in/api/stats/tasks');assert.equal(taskStats.status(),200,'Native tasks failed: '+email);
  const historical=await context.request.post('https://g2p-register.wverve.in/api/intake-form/get-intake-form-submission',{data:{submission_id:'718cc3ad-7f81-46cb-aea0-2696bb15e732',register_id:'a0000000-0000-4000-8000-000000000002'}});assert.equal(historical.status(),200,'Historical intake unavailable: '+email);
  const historicalData=await historical.json();assert(JSON.stringify(historicalData).includes('APPROVED'),'Historical approval missing: '+email);
  await page.screenshot({path:output+'/'+config.role+'.png',fullPage:true});
  results.push({email,role:config.role,nativeSignIn:true,nativeTasks:true,historicalApprovedIntake:true,permissions,url:new URL(page.url()).origin+new URL(page.url()).pathname});
  await context.close();
 }
 fs.writeFileSync(output+'/results.json',JSON.stringify({status:'passed',accounts:results},null,2));console.log(JSON.stringify({status:'passed',accounts:results.length}));
 }finally{await browser.close()}
})().catch(e=>{console.error(e.message);process.exitCode=1});
