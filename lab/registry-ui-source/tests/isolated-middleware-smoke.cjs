// Run only inside the standalone test image with --network none. No live accounts.
const http=require('node:http');
const assert=require('node:assert/strict');
const {spawn}=require('node:child_process');
if(process.env.MIDDLEWARE_ISOLATED_TEST!=='1')throw Error('Use the documented isolated Docker test command.');
const origin='http://127.0.0.1:3000';
const claims=Buffer.from(JSON.stringify({resource_access:{'register-staff-portal':{roles:['Registry Field Agent']}}})).toString('base64url');
const token=`test.${claims}.not-a-real-signature`;
let calls=[];
const backend=http.createServer(async(req,res)=>{
    const chunks=[];for await(const c of req)chunks.push(c);
    let body;try{body=JSON.parse(Buffer.concat(chunks).toString())}catch{}
    calls.push({url:req.url,id:req.headers['x-request-id'],authorization:req.headers.authorization,body});
    const json=(status,data)=>{res.writeHead(status,{'Content-Type':'application/json'});res.end(JSON.stringify(data))};
    const html=status=>{res.writeHead(status,{'Content-Type':'text/html'});res.end('<html>internal-upstream-detail-that-must-not-leak</html>')};
    if(req.url.startsWith('/auth/start_authentication_transaction'))return json(200,{redirectUrl:'http://127.0.0.1:4101/identity/authorize'});
    if(req.url==='/auth/get_logged_in_user'&&req.headers.authorization==='Bearer html-rejected-session')return html(401);
    if(req.url==='/auth/get_logged_in_user'&&req.headers.authorization==='Bearer invalid-jwt-shape')return json(200,{name:'Malformed isolated token'});
    if(req.headers.authorization!==`Bearer ${token}`)return json(401,{error:'invalid test session'});
    if(req.url==='/auth/get_logged_in_user')return json(200,{name:'Isolated field agent'});
    if(req.url.startsWith('/user-access/'))return json(200,[{permissions:['intakeSubmission:edit','intakeSubmission:view']}]);
    if(req.url==='/registration/api/registry/users')return html(403);
    if(req.url==='/registration/api/registry/offline-setup')return json(200,{account:'isolated-field-agent',qr_svg:'data:image/svg+xml;base64,PHN2Zy8+'});
    const mode=body?.request_body?.request_payload?.register_id;
    if(mode==='forbidden')return html(403);
    if(mode==='expired')return html(401);
    if(mode==='unavailable')return html(503);
    if(mode==='malformed')return html(200);
    if(req.url.includes('finalize_intake'))return json(200,{response_header:{response_status:'ERROR',response_error_code:'G2P-AUT-403',response_error_message:'Independent review required.'}});
    return json(200,{response_header:{response_status:'SUCCESS'},response_body:{response_payload:[{reference:'LOCAL-TEST'}],pagination_response:{number_of_items:1}}});
});
let app;
(async()=>{
    await new Promise(resolve=>backend.listen(4101,'127.0.0.1',resolve));
    app=spawn(process.execPath,['server.js'],{cwd:'/app',env:{...process.env,HOSTNAME:'127.0.0.1',PORT:'3000',APP_ORIGIN:origin,
        BACKEND_API_URL:'http://127.0.0.1:4101',MASTERDATA_BACKEND_API_URL:'http://127.0.0.1:4101',IAM_URL:'http://127.0.0.1:4101',
        NSIPA_REGISTRATION_URL:'http://127.0.0.1:4101/registration',APPLICATION_MNEMONIC:'registry-staff-portal',DEFAULT_LOCALE:'en'},stdio:['ignore','ignore','pipe']});
    let stderr='';app.stderr.on('data',c=>stderr+=c.toString());
    let ready=false;for(let i=0;i<100;i++){try{await fetch(origin+'/api/me');ready=true;break}catch{await new Promise(r=>setTimeout(r,100))}}
    assert(ready,'Standalone server did not start: '+stderr.slice(-1000));
    let checks=0;
    const verify=(ok,msg)=>{assert(ok,msg);checks++};
    const cookie=`X-Access-Token=${token}`;
    const post=(route,body={},headers={})=>fetch(origin+route,{method:'POST',headers:{Cookie:cookie,Origin:origin,'Content-Type':'application/json',...headers},body:JSON.stringify(body)});
    let r=await fetch(origin+'/api/me');verify(r.status===401,'Missing login must remain 401');
    verify(r.headers.get('cache-control')?.includes('no-store'),'Anonymous API response must not be cached');
    r=await fetch(origin+'/api/me',{headers:{Cookie:'X-ID-Token=test-id-only'}});verify(r.status===413,'Existing ID-token-only recovery must remain 413');
    r=await fetch(origin+'/api/me',{headers:{Cookie:'X-Access-Token=expired-test'}});verify(r.status===401,'IAM rejection must remain 401');
    r=await fetch(origin+'/api/me',{headers:{Cookie:'X-Access-Token=html-rejected-session'}});verify(r.status===401,'HTML IAM rejection must remain 401 without a server error');
    r=await fetch(origin+'/api/me',{headers:{Cookie:'X-Access-Token=invalid-jwt-shape'}});verify(r.status===401,'Malformed validated-token presentation data must fail safely');
    r=await fetch(origin+'/api/me',{headers:{Cookie:cookie}});verify(r.status===200&&(await r.json()).registry_scope==='field','IAM-validated field role must survive');
    verify(r.headers.get('x-content-type-options')==='nosniff','API nosniff header');
    verify(r.headers.get('referrer-policy')==='same-origin','API referrer policy');
    r=await fetch(origin+'/api/login?redirect_uri='+encodeURIComponent(origin+'/en/offline'),{redirect:'manual'});
    verify(r.status===307&&r.headers.get('location')==='http://127.0.0.1:4101/identity/authorize','Existing SSO initiation redirect must survive');
    r=await fetch(origin+'/',{redirect:'manual'});verify(r.status===307&&r.headers.get('location')?.endsWith('/en'),'Locale redirect must survive');
    const search='/api/intake-form/search-in-intake-form-submission';
    r=await post(search,{register_id:'normal'},{'X-Request-ID':'caller-controlled-id'});
    verify(r.status===200&&(await r.json()).submissions[0].reference==='LOCAL-TEST','Same-origin native list request must survive');
    const id=r.headers.get('x-request-id');verify(/^[\da-f-]{36}$/i.test(id)&&id!=='caller-controlled-id','Trace ID must be generated by Proxy');
    verify(calls.at(-1).id===id,'Backend must receive the same trace header');
    verify(calls.at(-1).authorization===`Bearer ${token}`,'Backend must retain the authenticated user token');
    const count=calls.length;
    r=await post(search,{register_id:'normal'},{Origin:'https://evil.example.test'});verify(r.status===403&&calls.length===count,'Cross-site request must be blocked before backend');
    r=await post(search,{}, {'Sec-Fetch-Site':'cross-site'});verify(r.status===403&&calls.length===count,'Cross-site Fetch Metadata must be blocked');
    r=await fetch(origin+search,{method:'POST',headers:{Cookie:cookie,'Content-Type':'application/json'},body:'{}'});verify(r.status===200,'Originless non-browser JSON compatibility');
    r=await post('/api/register/tabs',{register_id:'normal'});verify(r.status===200&&r.headers.get('cache-control')?.includes('no-store')&&!r.headers.get('cache-control')?.includes('public'),'Legacy public cache override must be removed');
    for(const [mode,status]of [['forbidden',403],['expired',401],['unavailable',502],['malformed',502]]){
        r=await post(search,{register_id:mode});const body=await r.text();verify(r.status===status&&!body.includes('internal-upstream-detail'),'Safe upstream status handling: '+mode);
    }
    r=await post('/api/intake-form/finalize-intake-form-submission',{submission_id:'LOCAL-TEST'});verify(r.status===403&&(await r.json()).error==='Independent review required.','Native approval denial and useful message must survive');
    r=await fetch(origin+'/api/registry-users',{headers:{Cookie:cookie}});verify(r.status===403,'Field agent must not gain administration access');
    r=await post('/api/offline/setup');verify(r.status===200&&(await r.json()).account==='isolated-field-agent','Private Collect setup proxy must remain available for the permitted mock user');
    verify(!stderr.includes('conflicting options'),'Authenticated requests must not retain conflicting revalidation settings');
    console.log(JSON.stringify({checks,passed:true,network:'none',backend:'local mock only',realCredentialsUsed:false}));
})().catch(e=>{console.error(e.stack);process.exitCode=1}).finally(async()=>{if(app)app.kill('SIGTERM');await new Promise(r=>backend.close(r));});
