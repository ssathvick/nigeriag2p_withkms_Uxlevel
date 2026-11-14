// Native record destinations, verified against the installed applications.
// The marker means an intentional operational journey, not a default landing.
export const origins={register:'register',registry:'registry',pbms:'pbms',awe:'awe',beneficiary:'beneficiary','portal-admin':'portal-admin',odk:'odk','master-data-ui':'master-data-ui','partner-management':'partner-management','consent-manager':'consent-manager','staff-portal':'staff-portal','iam-staff-ui':'iam-staff-ui',superset:'superset'};
export const defaults={register:'/en/register/household',registry:'/web#action=188',pbms:'/web#action=193',awe:'/requests',beneficiary:'/selfservice', 'portal-admin':'/web#action=393',odk:'/',geography:'/registration/geography',superset:'/superset/dashboard/nigeria-platform-analytics/','master-data-ui':'/en/geo-locations','partner-management':'/partners','consent-manager':'/approvals','staff-portal':'/en','iam-staff-ui':'/en/applications',knowledge:'/registration/knowledge',intake:'/registration/',review:'/registration/workspace',overview:'/registration/workspace'};
export function recordsUrl(service,metric='',category='',personal=false){
 if(service==='register')return markRecords('https://g2p.wverve.in/registration/mbr?view='+(metric==='change_request_status'?'changes':category.toLowerCase().includes('individual')?'individuals':'registers'));
 let path=defaults[service]||defaults.overview;
 const value=category.toLowerCase();
 if(service==='register')path=metric==='change_request_status'?'/en/change-request':value.includes('individual')?'/en/register/individual':defaults.register;
 if(service==='pbms')path='/web#action='+(metric&&metric!=='programme_status'?195:193);
 if(service==='registry')path='/web#action='+(metric==='household_membership_status'?191:value.includes('individual')?190:188);
 if(service==='portal-admin')path='/web#action='+({programme_lifecycle:393,cycle_lifecycle:397,entitlement_lifecycle:399,programme_membership_status:396}[metric]||393);
 if(service==='beneficiary'&&!personal&&metric){const id=metric==='programme_availability'?393:396;return markRecords('https://g2p-portal-admin.wverve.in/web#action='+id)}
 if(service==='beneficiary'&&personal&&['my_registration_status','my_application_status'].includes(metric))return markRecords('https://g2p.wverve.in/registration/');
 if(service==='beneficiary')path='/selfservice/en/applications';
 if(service==='master-data-ui')path=metric==='geographic_reference_levels'||value==='geographic levels'||!metric?'/en/geo-locations':'/en/reference-data';
 if(service==='partner-management')path=metric&&metric!=='partner_status'?'/requests':'/partners';
 if(service==='consent-manager')path=metric==='consent_artefact_status'?'/my/consents':metric==='consent_audit_inventory'?(value==='consent partners'?'/partners':'/decisions'):'/approvals';
 if(service==='knowledge'&&metric==='editorial_status')path='/registration/knowledge/admin';
 if(['intake','overview','review'].includes(service)&&metric)path='/registration/workspace';
 const host=origins[service]?'g2p-'+origins[service]+'.wverve.in':'g2p.wverve.in';
 return markRecords('https://'+host+path);
}
export function markRecords(href){const u=new URL(href,'https://g2p.wverve.in');u.searchParams.set('_nsipa_records','1');return u.href}
export const landingPaths={register:['/','/en'],registry:['/','/web'],pbms:['/','/web'],awe:['/','/policies'],'portal-admin':['/','/web'],beneficiary:['/','/selfservice','/selfservice/','/selfservice/en','/selfservice/en/home'],odk:['/'],superset:['/','/superset/welcome/'],'master-data-ui':['/','/en','/en/geo-locations'],'partner-management':['/','/partners'],'consent-manager':['/','/approvals','/my/consents'],'staff-portal':['/','/en'],'iam-staff-ui':['/','/en','/en/applications'],intake:['/registration/'],review:['/registration/workspace'],knowledge:['/registration/knowledge'],geography:['/registration/geography']};
export function landingService(href,referrer=''){
 const u=new URL(href);if(u.hash||[...u.searchParams.keys()].some(k=>k!=='db'))return null;
 // Preserve movement inside a native service and form return destinations.
 if(referrer){try{const r=new URL(referrer);if(r.origin===u.origin&&!/login|signin|callback|auth\//.test(r.pathname))return null}catch{}}
 return Object.keys(landingPaths).find(id=>u.hostname===(origins[id]?'g2p-'+origins[id]+'.wverve.in':'g2p.wverve.in')&&landingPaths[id].includes(u.pathname))||null;
}
