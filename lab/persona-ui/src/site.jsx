import React,{useState} from 'react';
import {createRoot} from 'react-dom/client';
import {modules,url} from './catalogue';
const isRegistry=m=>m.id==='register';
const homeContent={
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
const registryUrl='https://g2p-register.wverve.in/en';
function Site(){const [search,setSearch]=useState('');const visible=services.filter(m=>(m.title+' '+m.description+' '+m.group).toLowerCase().includes(search.toLowerCase()));const groups=[...new Set(visible.map(m=>m.group))];
return <><header className="hub-header"><a className="hub-brand" href="/" aria-label="NSIPA home"><img className="nsipa-nav-logo" src="/iqs-brand/nsipa-wordmark.svg" alt="NSIPA"/></a><nav aria-label="Platform navigation"><a href="https://g2p-register.wverve.in/en">Master Registry</a><a href="/territories/">Public territorial atlas</a><a href="/registration/analytics">Service dashboards</a><a href="https://g2p-register.wverve.in/en/offline">Field mobile apps</a></nav></header><main className="hub-main"><section aria-labelledby="services-title"><div className="hub-tools"><div><h2 id="services-title">All platform services</h2><p>{visible.length} services · Connected registry and programme services</p></div><label>Find a service<input type="search" placeholder="Search programmes, registry, consent…" value={search} onChange={e=>setSearch(e.target.value)}/></label></div>{groups.map(group=><section className="hub-group" key={group}><h3>{group}</h3><div className="hub-grid">{visible.filter(m=>m.group===group).map(m=><article className="hub-card" key={m.id}><span className="hub-eyebrow">{m.public?'PUBLIC SERVICE · NO LOGIN':'INTEGRATED APPLICATION'}</span><h4>{m.title}</h4><p>{m.description}</p>{!isRegistry(m)&&m.id!=='field-mobile'&&<a href={m.public?url(m):"/registration/analytics?service="+m.id}>{m.public?("Open public atlas →"):"Visual dashboard →"}</a>}<a href={isRegistry(m)?registryUrl:m.public||m.id==='field-mobile'?url(m):"/registration/analytics?service="+m.id}>{m.task} <span aria-hidden="true">↗</span></a></article>)}</div></section>)}{!visible.length&&<p className="hub-empty" role="status">No matching services. Try another search.</p>}</section></main><footer className="hub-footer">NSIPA · National Social Investment Programme Agency</footer></>}
createRoot(document.getElementById('site-root')).render(<Site/>);
