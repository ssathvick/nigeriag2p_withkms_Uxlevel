const {chromium}=require('playwright');
const {execFileSync}=require('node:child_process');
const fs=require('node:fs');const assert=require('node:assert/strict');
const fixtures=JSON.parse(fs.readFileSync('evidence/workflow-fixtures.json','utf8'));
function pdf(){const parts=['%PDF-1.4\n'];const objects=['<< /Type /Catalog /Pages 2 0 R >>','<< /Type /Pages /Kids [3 0 R] /Count 1 >>','<< /Type /Page /Parent 2 0 R /MediaBox [0 0 300 200] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>','<< /Length 78 >>\nstream\nBT /F1 12 Tf 20 100 Td (Synthetic React UAT verification. No real beneficiary.) Tj ET\nendstream','<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>'];const offsets=[0];for(let i=0;i<objects.length;i++){offsets.push(Buffer.byteLength(parts.join('')));parts.push(`${i+1} 0 obj\n${objects[i]}\nendobj\n`);}const offset=Buffer.byteLength(parts.join(''));parts.push(`xref\n0 6\n0000000000 65535 f \n${offsets.slice(1).map(x=>String(x).padStart(10,'0')+' 00000 n \n').join('')}trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n${offset}\n%%EOF\n`);return Buffer.from(parts.join(''));}
(async()=>{
const browser=await chromium.launch({headless:true,channel:'msedge'});const results=[];
try{for(const fixture of fixtures){
 const context=await browser.newContext({viewport:{width:1440,height:1000},acceptDownloads:true});
 const cookies=JSON.parse(execFileSync('wsl',['-d','Ubuntu-22.04','-u','root','--','python3','/mnt/h/Nigeria_Mosip/codex/openg2p-lab/pbms-react/verify-api.py','--browser-session','--host',fixture.host],{encoding:'utf8',stdio:['ignore','pipe','pipe']}));
 await context.addCookies(cookies);const page=await context.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));
 const base='https://'+fixture.host;await page.goto(base+'/pbms-ui/#approvals?program_id='+fixture.program_id);
 async function api(path,body={}){return page.evaluate(async({path,body})=>{const r=await fetch('/pbms-ui-api/'+path,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});return{status:r.status,data:await r.json()};},{path,body});}
 async function waitReady(id,payment=false){for(let i=0;i<36;i++){const r=await api('workflow/'+id);if(r.status!==200)throw new Error(JSON.stringify(r));const d=r.data;if(payment?d.list.disbursement_batch_creation_status==='complete':d.readiness.calculation_complete)return d;if(i%6===0)console.log(fixture.host,'waiting',id,payment?'payment submission':'calculation',d.list.eligibility_process_status,d.list.entitlement_process_status);await new Promise(r=>setTimeout(r,5000));}throw new Error('Workflow processing timed out: '+id);}
 async function openQueue(key){await page.goto(base+'/pbms-ui/#'+key+'?program_id='+fixture.program_id);await page.getByRole('button',{name:'Open →'}).first().waitFor();await page.getByRole('button',{name:'Open →'}).first().click();await page.getByText('Verification evidence',{exact:true}).waitFor();}
 async function verificationAndApproval(kind,id){
  const denied=await api('approve/'+id);assert.equal(denied.status,409,'Approval must be rejected before evidence');
  await page.getByRole('button',{name:'Verification',exact:true}).click();
  await page.getByLabel('Verification comment').fill('Synthetic React UAT: checked exactly one fictional beneficiary and NGN 1 entitlement.');
  await page.getByLabel('Supporting PDF').setInputFiles({name:'synthetic-verification.pdf',mimeType:'application/pdf',buffer:pdf()});
  await page.getByRole('button',{name:'Record verification',exact:true}).click();
  await page.getByText('Verification recorded.',{exact:true}).waitFor();
  const downloadPromise=page.waitForEvent('download');await page.getByRole('button',{name:'Download evidence'}).first().click();const download=await downloadPromise;const file=await download.path();assert.deepEqual(fs.readFileSync(file),pdf(),'Uploaded PDF round-trips through existing document store');
  await page.getByRole('button',{name:kind==='disbursement'?'Approve for disbursement':'Approve enrollment',exact:true}).click();
  await page.getByRole('button',{name:'Confirm approval',exact:true}).click();
  await page.getByText(kind==='disbursement'?'Approved for disbursement. PBMS will process payment instructions; refresh to follow progress.':'Enrollment approved.',{exact:true}).waitFor();
  const replay=await api('approve/'+id);assert.equal(replay.status,200);assert.equal(replay.data.already_approved,true);
 }
 const enrollment=await waitReady(fixture.enrollment_list_id);
 if(!enrollment.readiness.approved){await openQueue('approvals');await verificationAndApproval('enrollment',fixture.enrollment_list_id);await page.screenshot({path:`evidence/${fixture.host}-enrollment-approved.png`,fullPage:true});await page.getByRole('button',{name:'Close workflow'}).click();}
 if(!fixture.disbursement_list_id){
 await page.goto(base+'/pbms-ui/#disbursement?program_id='+fixture.program_id);await page.getByRole('button',{name:'New record'}).click();
 await page.getByLabel('Cycle Mnemonic',{exact:true}).fill(fixture.tag+'_PAY');await page.getByLabel('Disbursement Schedule Date',{exact:false}).fill(new Date().toLocaleDateString('en-CA',{timeZone:'Asia/Kolkata'}));
 let responsePromise=page.waitForResponse(r=>r.url().endsWith('/g2p.disbursement.cycle/create'));await page.getByRole('button',{name:'Save record',exact:true}).click();let response=await responsePromise;const cycle=(await response.json()).result;assert(Number.isInteger(cycle));fixture.disbursement_cycle_id=cycle;
 await page.getByText('Record saved successfully.').waitFor();
 await page.goto(base+'/pbms-ui/#lists?disbursement_cycle_id='+cycle);await page.getByRole('button',{name:'New record'}).click();await page.getByLabel('Mnemonic',{exact:true}).fill(fixture.tag+'_PAYLIST');await page.getByLabel('Brief',{exact:true}).fill('Synthetic React workflow test. One fictional beneficiary. Local Example Bank only.');
 responsePromise=page.waitForResponse(r=>r.url().endsWith('/g2p.beneficiary.list/create'));await page.getByRole('button',{name:'Save record',exact:true}).click();response=await responsePromise;const list=(await response.json()).result;assert(Number.isInteger(list));fixture.disbursement_list_id=list;fs.writeFileSync('evidence/workflow-fixtures.json',JSON.stringify(fixtures,null,2));
 await page.getByText('Record saved successfully.').waitFor();}
 const list=fixture.disbursement_list_id;let data=await waitReady(list);assert.equal(data.list.number_of_registrants,1);
 await openQueue('payments');if(!data.readiness.approved)await verificationAndApproval('disbursement',list);data=await waitReady(list,true);assert.equal(data.batches.length,1);assert.equal(data.envelopes.length,1);assert.equal(data.batches[0].total_disbursement_quantity,1);
 await page.getByRole('button',{name:'Refresh workflow',exact:true}).click();await page.getByRole('button',{name:'Refresh workflow',exact:true}).waitFor();await page.getByRole('button',{name:'Payments',exact:true}).click();await page.getByRole('button',{name:'View report'}).last().click();await page.getByRole('heading',{name:'Payment status report'}).waitFor();await page.screenshot({path:`evidence/${fixture.host}-payment-report.png`,fullPage:true});
 await page.getByRole('button',{name:'Close report'}).click();await page.getByRole('button',{name:'Beneficiaries',exact:true}).click();await page.getByText('Page 1',{exact:true}).waitFor();
 assert.deepEqual(errors,[]);assert(page.url().includes('/pbms-ui/'));results.push({host:fixture.host,enrollment:'approved',verification:'PDF upload/download passed',disbursement:'approved',quantity:1,batches:1,duplicate_approval:'idempotent',before_evidence:'rejected',react_only:true});
 await context.close();console.log('PASS',fixture.host,'enrollment → verification → approval → disbursement → Bridge report');
}
fs.writeFileSync('evidence/workflow-browser-results.json',JSON.stringify(results,null,2));
}finally{await browser.close();}
})().catch(e=>{console.error(e.stack);process.exitCode=1;});
