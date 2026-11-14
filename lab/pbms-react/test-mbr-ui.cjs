const {chromium}=require('playwright');
const {execFileSync}=require('child_process');
const fs=require('fs');
const assert=require('assert/strict');
const creds=JSON.parse(execFileSync('wsl',['-d','Ubuntu-22.04','-u','root','--','cat','/opt/openg2p-lab/registration/mbr-demo-credentials.json'],{encoding:'utf8',stdio:['ignore','pipe','pipe']}));
const base='https://g2p.wverve.in/registration/mbr';
const out='H:/Nigeria_Mosip/codex/output/mbr-verification';fs.mkdirSync(out,{recursive:true});
const ids=[];let nativeId=null,checks=0;
async function main(){
 const browser=await chromium.launch({channel:'msedge',headless:true});
 const pages={};const errors=[];
 try{
  for(const email of Object.keys(creds)){
   const context=await browser.newContext({viewport:{width:1440,height:1050},ignoreHTTPSErrors:true});
   const page=await context.newPage();pages[email]=page;page.on('pageerror',e=>errors.push(e.message));
   await page.goto(base,{waitUntil:'domcontentloaded'});
   await page.locator('#username').waitFor({timeout:45000});
   await page.locator('#username').fill(email);await page.locator('#password').fill(creds[email].password);
   await page.locator('input[type=submit],button[type=submit]').first().click();
   await page.getByRole('heading',{name:'Your registry workspace'}).waitFor({timeout:45000});
   assert.equal(new URL(page.url()).pathname,'/registration/mbr');checks++;
   console.log('Signed in and loaded '+creds[email].role);
  }
  const officer=pages['aarin@gmail.com'],l1=pages['abutu@gmail.com'],l2=pages['adaku@gmail.com'],admin=pages['admin@openg2p.org'],field=pages['abuchi@gmail.com'];
  async function api(page,path,payload){return page.evaluate(async({path,payload})=>{
   const root=document.querySelector('#mbr-root');const options=payload?{method:'POST',body:new URLSearchParams({csrf:root.dataset.csrf,payload:JSON.stringify(payload)})}:{};
   const response=await fetch(root.dataset.prefix+'/api'+path,options);return {status:response.status,data:await response.json()};
  },{path,payload})}
  const boot=(await api(officer,'/bootstrap')).data;
  assert(boot.masters.length>0);checks++;
  await officer.locator('.mbr-pill').filter({hasText:'Households'}).click();
  await officer.getByRole('heading',{name:'Household Register',exact:true}).waitFor();
  assert.equal(new URL(officer.url()).searchParams.get('view'),'registers');checks++;
  await officer.locator('.mbr-sidebar').getByRole('link',{name:'Overview'}).click();
  await officer.getByRole('button',{name:'＋ New household intake',exact:true}).click();
  await officer.getByLabel('Survey sponsor').selectOption('NG CARES');
  await officer.getByRole('radio',{name:'Yes',exact:true}).check();
  await officer.locator('.mbr-section-heading>button[aria-expanded]').filter({hasText:'Household Member Details'}).click();
  await officer.getByRole('button',{name:'＋ Add member'}).click();
  await officer.locator('#mbr-member-surname').fill('E2E Synthetic');
  await officer.locator('#mbr-member-first_name').fill('Workflow');
  await officer.locator('#mbr-member-relationship').selectOption('Head of Household');
  await officer.locator('#mbr-member-sex').selectOption('Female');
  await officer.locator('#mbr-member-age').fill('36');
  await officer.getByRole('group',{name:'Valid NIN available?'}).getByRole('radio',{name:'Yes',exact:true}).check();
  await officer.locator('#mbr-member-nin').fill('00000000009');
  await officer.getByRole('button',{name:'Save member',exact:true}).click();
  await officer.getByRole('button',{name:'Save draft',exact:true}).click();
  await officer.getByText('Draft saved.',{exact:true}).waitFor();checks++;
  const draftBoot=(await api(officer,'/bootstrap')).data;
  const draft=draftBoot.submissions.find(s=>s.payload.members.some(m=>m.surname==='E2E Synthetic'));assert(draft);ids.push(draft.id);
  // Use a complete synthetic payload to exercise both SSO approval stages.
  const data={consent:'Yes',sponsor:'NG CARES',enumerator:'Aarin',state:'Kano',zone:'North West',community:'E2E Synthetic Community',serial_number:'MBR-E2E',address:'E2E synthetic address',number_heads:1,complete_members:'Yes',members:draft.payload.members,roof:'Metal sheets',floor:'Cement',rooms:2,water:'Borehole',lighting:'Solar',cooking_fuel:'Gas',income_source:'Trading',monthly_income:10000,shocks:[],health_insurance:'No',assets:Object.fromEntries(boot.configuration.assets.map(a=>[a,'No'])),grows_crops:'No',crops:[]};
  let response=await api(officer,'/submissions/'+draft.id+'/save',{data,submit:true,version:draft.version});assert.equal(response.status,200);checks++;
  await l1.goto(base+'?view=tasks&status=Pending&id='+draft.id);
  await l1.getByRole('button',{name:'Approve → Stage 2',exact:true}).waitFor();
  const uuid=l1.locator('.mbr-metadata code');assert((await uuid.innerText()).startsWith('••'));checks++;
  await l1.getByRole('button',{name:'Reveal submission UUID'}).click();assert.equal(await uuid.innerText(),draft.id);checks++;
  await l1.getByRole('tab',{name:'Existing Duplicates',exact:true}).click();await l1.getByRole('tabpanel').getByRole('heading',{name:'Existing Duplicates'}).waitFor();checks++;
  await l1.getByRole('tab',{name:'Intake Form',exact:true}).click();
  await l1.getByRole('button',{name:'Reject',exact:true}).click();
  assert(await l1.getByRole('radio',{name:/Return for correction/}).isChecked());
  assert(await l1.getByRole('button',{name:'Confirm decision'}).isDisabled());checks++;
  await l1.getByRole('button',{name:'Cancel',exact:true}).click();
  await l1.getByRole('button',{name:'Approve → Stage 2',exact:true}).click();
  await l1.locator('.mbr-badge').filter({hasText:'Pending · Stage 2'}).waitFor();checks++;
  await l2.goto(base+'?view=tasks&status=Pending&id='+draft.id);
  await l2.getByRole('button',{name:'Final Approve',exact:true}).click();
  await l2.locator('.mbr-badge.approved').waitFor();
  const approved=(await api(l2,'/submissions/'+draft.id)).data;assert.equal(approved.state,'APPROVED');nativeId=approved.master_id;checks++;
  await officer.goto(base+'?view=registers&id='+nativeId);
  await officer.getByRole('button',{name:'Edit Details',exact:true}).waitFor();checks++;
  await officer.screenshot({path:out+'/approved-household.png',fullPage:true});
  await officer.getByRole('button',{name:'Edit Details',exact:true}).click();
  await officer.locator('#mbr-community').fill('E2E Updated Community');
  await officer.getByRole('button',{name:'Submit change request',exact:true}).click();
  await officer.getByRole('tab',{name:'New & Old Values',exact:true}).waitFor();
  const changes=(await api(officer,'/bootstrap')).data.submissions.filter(s=>s.kind==='change'&&s.master_id===nativeId);
  assert.equal(changes.length,1);const change=changes[0];ids.push(change.id);
  await officer.getByRole('tab',{name:'New & Old Values',exact:true}).click();
  await officer.getByRole('tabpanel').getByText('E2E Updated Community',{exact:true}).waitFor();checks++;
  assert.equal((await api(officer,'/bootstrap')).data.masters.find(h=>h.id===nativeId).payload.community,'E2E Synthetic Community');checks++;
  await l1.goto(base+'?view=tasks&status=Pending&id='+change.id);await l1.getByRole('button',{name:'Approve → Stage 2',exact:true}).click();
  await l1.locator('.mbr-badge').filter({hasText:'Pending · Stage 2'}).waitFor();
  await l2.goto(base+'?view=tasks&status=Pending&id='+change.id);await l2.getByRole('button',{name:'Final Approve',exact:true}).click();
  await l2.locator('.mbr-badge.approved').waitFor();
  assert.equal((await api(officer,'/bootstrap')).data.masters.find(h=>h.id===nativeId).payload.community,'E2E Updated Community');checks++;
  await admin.locator('.mbr-sidebar').getByRole('link',{name:'Analytics Dashboard'}).click();
  await admin.getByRole('heading',{name:'Gender / age pyramid'}).waitFor();
  assert.deepEqual(await admin.locator('.mbr-pyramid-row>strong').allTextContents(),['0–4','5–17','18–34','35–59','60+']);checks++;
  await admin.screenshot({path:out+'/analytics-desktop.png',fullPage:true});checks++;
  await field.getByRole('button',{name:/Offline Field Sync Simulator/}).first().click();
  await field.getByRole('dialog').getByRole('heading',{name:'Offline Field Sync Simulator',exact:true}).waitFor();
  await field.getByRole('button',{name:'Close dialog'}).click();checks++;
  await officer.goto(base);await officer.getByRole('heading',{name:'Your registry workspace'}).waitFor();
  await officer.locator('#ng-km-launcher').click();await officer.getByRole('dialog',{name:'Knowledge Management'}).waitFor();
  await officer.keyboard.press('Escape');assert.equal(await officer.getByRole('dialog',{name:'Knowledge Management'}).count(),0);checks++;
  await officer.screenshot({path:out+'/dashboard-desktop.png',fullPage:true});
  await officer.setViewportSize({width:390,height:844});await officer.screenshot({path:out+'/dashboard-mobile.png',fullPage:true});
  assert(await officer.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));checks++;
  assert.equal(errors.length,0,errors.join('\n'));
  const denied=await api(admin,'/submissions/'+draft.id+'/decision',{action:'approve',version:approved.version});assert.equal(denied.status,403);checks++;
  fs.writeFileSync(out+'/ui-results.json',JSON.stringify({checks,status:'passed',roles:Object.keys(creds),consoleErrors:errors},null,2));
  console.log(JSON.stringify({checks,status:'passed',screenshots:out}));
 }catch(e){for(const [email,page] of Object.entries(pages)){await page.screenshot({path:out+'/failure-'+email.split('@')[0]+'.png',fullPage:true}).catch(()=>{});}throw e}
 finally{
  await browser.close();
  fs.writeFileSync(out+'/cleanup-ids.json',JSON.stringify({submissions:ids,master:nativeId}));
  // Cleanup is handled by a parameterized PG script and only these exact generated IDs.
 }
}
main().catch(e=>{console.error(e.message);process.exitCode=1});
