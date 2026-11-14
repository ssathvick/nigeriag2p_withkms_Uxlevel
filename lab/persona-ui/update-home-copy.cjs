const fs=require('fs');let s=fs.readFileSync('src/site.jsx','utf8');const a=s.indexOf('const services='),b=s.indexOf('const registryUrl=',a);s=s.slice(0,a)+`const homeContent={
 'register':{title:'Master Registry',description:'Register households and individuals, resume drafts, correct returned cases, review change requests, and complete two-stage approvals with a preserved history.',task:'Open Master Registry'},
 'field-mobile':{title:'Mobile field registration',host:'g2p-register.wverve.in',path:'/en/offline',public:false,description:'Set up mobile household collection from the Master Registry. Submitted field records enter the same intake and approval workflow.',task:'Open mobile registration setup'},
 'territories':{description:'Explore Nigeria’s administrative areas, population, poverty and public investment using source-labelled public data.'},
 'knowledge':{description:'Find guidance for household intake, corrections, registry reviews and the services supporting your work.'},
 'beneficiary':{description:'Access beneficiary self-service forms and follow programme applications.'},
 'pbms':{description:'Manage programme enrolment, benefits and disbursements. Registry approval remains separate from programme eligibility and payment approval.'},
 'portal-admin':{description:'Maintain programmes and application settings used by the Beneficiary portal.'},
 'odk':{description:'Manage field collection projects, forms and submissions. Household submissions follow the integrated Master Registry review process.'},
 'geography':{description:'Inspect available household registration counts by zone, state and recorded local government area.'},
 'superset':{description:'View service dashboards, operational status and workflow guidance usage across the platform.'},
 'master-data-ui':{description:'Maintain shared locations and reference attributes used across registry and programme services.'},
 'partner-management':{description:'Manage partner onboarding and access to connected platform services.'},
 'consent-manager':{description:'Review consent records and manage data access policies.'},
 'staff-portal':{description:'Find staff applications and sign in with your authorised account. Manage household intake and registry reviews in the Master Registry.'},
 'iam-staff-ui':{description:'Manage staff accounts and application access with the required permissions. Registry roles and onboarding are available in the Master Registry.'}
};
const services=modules.filter(m=>!['jos-cct','intake','review','registry','awe'].includes(m.id)).map(m=>({...m,...homeContent[m.id]}));
`+s.slice(b);s=s.replace('href="/field-preview/android/"','href="https://g2p-register.wverve.in/en/offline"').replace('Existing application workflows','Connected registry and programme services').replace("!isRegistry(m)&&m.host==='g2p.wverve.in'?'PERSONA WORKSPACE':",'');s=s.replace("m.id==='jos-cct'?\"Open pilot demo →\":m.id==='field-mobile'?\"Open mobile apps →\":",'');s=s.replace('m.public?url(m):"/registration/analytics?service="+m.id}>{m.task}',"m.public||m.id==='field-mobile'?url(m):\"/registration/analytics?service=\"+m.id}>{m.task}");fs.writeFileSync('src/site.jsx',s);
