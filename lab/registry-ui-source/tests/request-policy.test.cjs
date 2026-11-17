const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const ts=require('typescript');

// Compile the dependency-free policy in memory; no live services or test credentials.
const file=path.join(__dirname,'../src/shared/security/request-policy.ts');
const compiled=ts.transpileModule(fs.readFileSync(file,'utf8'),{compilerOptions:{module:ts.ModuleKind.CommonJS}});
const sandbox={exports:{},URL,Headers};
vm.runInNewContext(compiled.outputText,sandbox,{filename:file});
const {isAllowedBrowserRequest:allowed,applicationOrigin}=sandbox.exports;
const request=(headers={},method='POST',url='https://registry.example.test/api/intake')=>({method,url,headers:new Headers(headers)});

test('ordinary same-origin JSON and multipart submissions remain available',()=>{
    for(const type of ['application/json','multipart/form-data; boundary=upload']){
        assert.equal(allowed(request({origin:'https://registry.example.test','content-type':type,'sec-fetch-site':'same-origin'})),true);
    }
});
test('cross-origin, sibling-site and opaque browser writes are rejected',()=>{
    for(const origin of ['https://evil.example.test','https://registry.example.test.evil.test','null','file:///tmp/form','https://user@registry.example.test']){
        assert.equal(allowed(request({origin,'content-type':'application/json'})),false,origin);
    }
});
test('Fetch Metadata blocks cross-site writes even if another header claims same-origin',()=>{
    assert.equal(allowed(request({origin:'https://registry.example.test','sec-fetch-site':'cross-site'})),false);
    assert.equal(allowed(request({'sec-fetch-site':'same-site','content-type':'application/json'})),false);
});
test('same-origin Referer fallback works; cross-origin Referer does not',()=>{
    assert.equal(allowed(request({referer:'https://registry.example.test/en/offline'})),true);
    assert.equal(allowed(request({referer:'https://evil.example.test/form','content-type':'application/json'})),false);
});
test('Origin takes precedence over a forged same-origin Referer',()=>{
    assert.equal(allowed(request({origin:'https://evil.example.test',referer:'https://registry.example.test/en'})),false);
});
test('non-browser JSON clients retain compatibility but originless simple forms are denied',()=>{
    assert.equal(allowed(request({'content-type':'application/json; charset=utf-8'})),true);
    for(const type of ['application/x-www-form-urlencoded','text/plain','multipart/form-data; boundary=x']){
        assert.equal(allowed(request({'content-type':type})),false,type);
    }
});
test('safe navigation, SSO callbacks and preflights are not turned into write requests',()=>{
    for(const method of ['GET','HEAD','OPTIONS'])assert.equal(allowed(request({origin:'https://identity.example.test','sec-fetch-site':'cross-site'},method)),true);
});
test('the canonical configured origin works behind an internal reverse proxy',()=>{
    const req=request({host:'internal:3000',origin:'https://registry.example.test'},'POST','http://internal:3000/api/intake');
    assert.equal(allowed(req,'https://registry.example.test'),true);
    assert.equal(allowed(req,'not a URL'),false);
});
test('trusted Host/protocol work without trusting X-Forwarded-Host',()=>{
    const req=request({host:'registry.example.test','x-forwarded-proto':'https','x-forwarded-host':'evil.example.test',origin:'https://registry.example.test'},'POST','http://internal:3000/api/intake');
    assert.equal(applicationOrigin(req),'https://registry.example.test');
    assert.equal(allowed(req),true);
    req.headers.set('origin','https://evil.example.test');
    assert.equal(allowed(req),false);
});
test('invalid proxy headers fail closed and default ports normalize correctly',()=>{
    assert.equal(allowed(request({host:'registry.example.test,evil.test',origin:'https://registry.example.test'})),false);
    assert.equal(allowed(request({'x-forwarded-proto':'https,http',origin:'https://registry.example.test'})),false);
    assert.equal(allowed(request({origin:'https://registry.example.test:443'})),true);
});
