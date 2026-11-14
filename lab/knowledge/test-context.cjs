const assert=require('node:assert/strict');
const {resolve,guideMappings,relatedGuides}=require('./context.js');
const seed=require('../knowledge-seed.json');
const cases=[
 [{path:'/registration/profile'},'intake','Household details'],
 [{path:'/registration/profile',status:'rejected'},'intake','Correct returned details'],
 [{path:'/registration/profile',section:'Household members'},'intake','Household members'],
 [{path:'/registration/profile',section:'Optional household coordinates'},'intake','Capture household coordinates'],
 [{path:'/registration/staff/profile/test'},'review','Verification checks'],
 [{path:'/registration/workspace',status:'rejected',persona:'officer'},'intake','Correct returned details'],
 [{path:'/registration/workspace',status:'pending_review',persona:'verifier'},'review','Verification checks'],
 [{path:'/registration/workspace',status:'pending_review',persona:'citizen'},'review','Awaiting review'],
 [{path:'/registration/workspace',status:'approved'},'beneficiary','Programme application'],
 [{path:'/registration/workspace',view:'applications',persona:'citizen'},'beneficiary','Application status'],
 [{path:'/registration/workspace',view:'applications',status:'eligible',persona:'supervisor'},'pbms','Enrollment'],
 [{path:'/registration/workspace',view:'activity',persona:'supervisor'},'review','Recorded activity'],
 [{path:'/registration/geography'},'geography','State record map'],
 [{path:'/registration/geography',section:'Household location points'},'geography','Household location points'],
 [{path:'/registration/geography',section:'Location coverage'},'geography','Location coverage'],
 [{hostname:'register.nigeriag2p.com',path:'/en/register/individual/id'},'register','Individual details'],
 [{hostname:'register.nigeriag2p.com',path:'/en/register/household/id'},'register','Household details'],
 [{hostname:'register.nigeriag2p.com',path:'/en/tasks/intake-form'},'register','Submit for approval'],
 [{hostname:'beneficiary.nigeriag2p.com',path:'/en/programs/apply/1'},'beneficiary','Programme application'],
 [{hostname:'beneficiary.nigeriag2p.com',path:'/en/applications'},'beneficiary','Application status'],
 [{hostname:'awe.nigeriag2p.com',path:'/requests/abc'},'awe','Review evidence'],
 [{hostname:'awe.nigeriag2p.com',path:'/policies'},'awe','Policy versions'],
 [{hostname:'pbms.nigeriag2p.com',path:'/web',hash:'#model=g2p.enrollment.cycle'},'pbms','Enrollment'],
 [{hostname:'pbms.nigeriag2p.com',path:'/web',hash:'#model=g2p.program.definition'},'pbms','Programme setup'],
 [{hostname:'pbms.nigeriag2p.com',path:'/web',hash:'#model=g2p.entitlement'},'pbms','Benefit calculation'],
 [{hostname:'pbms.nigeriag2p.com',path:'/web',hash:'#model=g2p.payment'},'pbms','Disbursement'],
 [{hostname:'portal-admin.nigeriag2p.com',hash:'#model=g2p.program'},'portal-admin','Programme configuration'],
 [{hostname:'registry.nigeriag2p.com',hash:'#model=res.partner'},'registry','Record maintenance'],
 [{hostname:'superset.nigeriag2p.com',path:'/superset/dashboard/2/'},'superset','Choose dashboard'],
 [{hostname:'consent-manager.nigeriag2p.com',section:'Withdraw consent'},'consent-manager','Consent withdrawal'],
 [{hostname:'iam-staff-ui.nigeriag2p.com',section:'Role assignment'},'iam-staff-ui','Role assignment'],
 [{path:'/registration/knowledge/admin'},'knowledge','Review and publication'],
 [{path:'/registration/knowledge/admin/7/history/3'},'knowledge','Version history'],
 [{hostname:'pbms.nigeriag2p.com',path:'/unknown'},'pbms','Service overview'],
 [{path:'/registration/workspace',status:'pending_review',persona:'verifier',explicit:{module:'review',stage:'Approve or return'}},'review','Approve or return']
];
for(const [input,module,stage]of cases){const actual=resolve(input);assert.equal(actual.module,module,JSON.stringify(input));assert.equal(actual.stage,stage,JSON.stringify(input));assert(seed.articles.some(a=>a.module===module&&a.stage===stage),'Missing published seed: '+module+'/'+stage);}
assert.equal(resolve({persona:'invented'}).audience,'all');
assert.equal(resolve({persona:'citizen'}).audience,'citizen');
console.log(cases.length+' context mappings passed; every mapping has guidance.');

const pack=require('./documentation-pack.json').articles;
assert.equal(guideMappings.length,64);
assert.deepEqual(new Set(guideMappings.map(m=>m.slug)),new Set(pack.map(a=>a.slug)));
for(const mapping of guideMappings){
 assert(seed.articles.some(a=>a.module===mapping.module&&a.stage===mapping.stage),mapping.stage);
 for(const context of mapping.contexts){
  assert(seed.articles.some(a=>a.module===mapping.module&&a.stage===context),mapping.module+'/'+context);
  assert(relatedGuides({module:mapping.module,stage:context}).some(a=>a.slug===mapping.slug),'Unreachable guide '+mapping.slug);
 }
}
const detailed=[
 [{hostname:'register.nigeriag2p.com',path:'/en/register/individual/123/version-history'},'register','Committed record history'],
 [{hostname:'register.nigeriag2p.com',path:'/en/tasks/change-request/123'},'register','Proposed and approved changes'],
 [{hostname:'register.nigeriag2p.com',path:'/en/incoming-messages'},'register','Ingestion monitoring'],
 [{hostname:'register.nigeriag2p.com',path:'/en/intake-form/individual/new/123'},'register','Registry intake lifecycle'],
 [{hostname:'registry.nigeriag2p.com',section:'Import records'},'registry','CSV import validation'],
 [{hostname:'registry.nigeriag2p.com',section:'ID Types'},'registry','Identifier type configuration'],
 [{hostname:'pbms.nigeriag2p.com',section:'Verify eligibility'},'pbms','Eligibility reassessment'],
 [{hostname:'pbms.nigeriag2p.com',section:'PMT Configuration'},'pbms','Proxy means test configuration'],
 [{hostname:'pbms.nigeriag2p.com',section:'Program Funds'},'pbms','Programme fund records'],
 [{hostname:'pbms.nigeriag2p.com',section:'Cycle Manager'},'pbms','Cycle manager configuration'],
 [{hostname:'awe.nigeriag2p.com',path:'/policies/registry.change_request/versions/1/edit'},'awe','Policy versions'],
 [{hostname:'awe.nigeriag2p.com',section:'Reassign task'},'awe','Task reassignment'],
 [{hostname:'awe.nigeriag2p.com',section:'SLA hours'},'awe','Overdue approval tasks'],
 [{hostname:'consent-manager.nigeriag2p.com',section:'Partner policy'},'consent-manager','Partner policy scope'],
 [{hostname:'consent-manager.nigeriag2p.com',section:'Consent revocation'},'consent-manager','Consent withdrawal and expiry'],
 [{hostname:'partner-management.nigeriag2p.com',section:'Rotate keys'},'partner-management','Partner lifecycle and keys'],
 [{hostname:'master-data-ui.nigeriag2p.com',section:'Attributes'},'master-data-ui','Reference code lists'],
 [{hostname:'iam-staff-ui.nigeriag2p.com',section:'Login Providers'},'iam-staff-ui','Application and login provider configuration'],
 [{hostname:'superset.nigeriag2p.com',section:'Import dashboards'},'superset','Dashboard import preparation'],
 [{path:'/registration/geography',section:'Coordinate provenance'},'geography','Coordinate quality'],
 [{path:'/registration/ai'},'knowledge','Ask local AI'],
 [{path:'/registration/profile',section:'Registration readiness',explicit:{module:'intake',stage:'Household members'}},'intake','Household members']
];
for(const [input,module,stage]of detailed){const actual=resolve(input);assert.equal(actual.module,module,JSON.stringify(input));assert.equal(actual.stage,stage,JSON.stringify(input));}
assert(resolve({hostname:'pbms.nigeriag2p.com',path:'/unknown'}).related.some(m=>m.stage==='Programme fund records')===false);
assert(resolve({path:'/registration/geography'}).related.some(m=>m.stage==='Map intensity and counting'));
console.log(detailed.length+' detailed screen checks passed; all 64 added guides have reachable stage mappings.');
