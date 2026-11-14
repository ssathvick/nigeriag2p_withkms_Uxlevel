'use client';
import {useState, type ReactNode} from 'react';
import {Link,useRouter} from '@/i18n/navigation';
import {useRegister} from '@/context/RegisterContext';
import {useRbac} from '@/context/RbacContext';
import {useFetch} from '@/shared/hooks/useFetch';
import {useIntakeForms} from '@/features/intake-form/hooks/useIntakeForms';
import styles from './registry-dashboard.module.css';

type IconName='home'|'people'|'form'|'change'|'task'|'offline'|'staff'|'arrow'|'refresh'|'search';
function Icon({name}:{name:IconName}){
 const paths:Record<IconName,ReactNode>={
  home:<><path d="m3 10 9-7 9 7v10a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1Z"/><path d="M9 21v-8h6v8"/></>,
  people:<><circle cx="9" cy="8" r="3"/><path d="M3 21v-3a6 6 0 0 1 12 0v3M17 5a3 3 0 0 1 0 6M17 15a5 5 0 0 1 4 5"/></>,
  form:<><path d="M14 3H5v18h14V8ZM14 3v5h5M8 12h8M8 16h5"/></>,
  change:<><path d="M20 8A8 8 0 0 0 6 5L3 8m0-5v5h5M4 16a8 8 0 0 0 14 3l3-3m0 5v-5h-5"/></>,
  task:<><rect x="4" y="5" width="16" height="16" rx="3"/><path d="M9 5V3h6v2M8 13l3 3 5-6"/></>,
  offline:<><rect x="7" y="2" width="10" height="20" rx="2"/><path d="m9 12 2 2 4-4M10 18h4"/></>,
  staff:<><circle cx="9" cy="7" r="3"/><path d="M3 19v-2a6 6 0 0 1 10-4M18 11l4 2v3c0 3-4 5-4 5s-4-2-4-5v-3Z"/></>,
  arrow:<path d="M5 12h14m-5-5 5 5-5 5"/>,refresh:<><path d="M20 7v5h-5M4 17v-5h5M6 6a8 8 0 0 1 13 3M5 15a8 8 0 0 0 13 3"/></>,search:<><circle cx="10" cy="10" r="6"/><path d="m15 15 6 6"/></>,
 };
 return <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">{paths[name]}</svg>;
}
function Action({href,allowed,children,icon,primary=false}:{href:string;allowed:boolean;children:ReactNode;icon:IconName;primary?:boolean}){
 const cls=styles.action+(primary?' '+styles.primary:'');
 return allowed?<Link href={href} className={cls}><Icon name={icon}/>{children}<Icon name="arrow"/></Link>:null;
}
function Metric({label,value,href,icon,allowed=true,loading=false,failed=false}:{label:string;value:unknown;href:string;icon:IconName;allowed?:boolean;loading?:boolean;failed?:boolean}){
 const text=!allowed?'—':loading?'…':failed?'Unavailable':new Intl.NumberFormat('en-NG').format(Number(value??0));
 const content=<><span className={styles.metricIcon}><Icon name={icon}/></span><span className={styles.metricValue}>{text}</span><span className={styles.metricLabel}>{label}</span><span className={styles.metricFoot}>{allowed?'Open records':'Not available for your role'}{allowed&&<Icon name="arrow"/>}</span></>;
 return allowed?<Link href={href} className={styles.metric} aria-label={`${label}: ${text}. Open records.`} aria-busy={loading}>{content}</Link>:null;
}
function Panel({id,title,subtitle,icon,tag,tone='',children}:{id:string;title:string;subtitle:string;icon:IconName;tag:string;tone?:string;children:ReactNode}){
 return <section className={[styles.panel,styles[tone]].filter(Boolean).join(' ')} aria-labelledby={id}><div className={styles.panelHead}><span className={styles.panelIcon}><Icon name={icon}/></span><div><h2 id={id}>{title}</h2><p>{subtitle}</p></div><span className={styles.tag}>{tag}</span></div>{children}</section>;
}
function Dashboard(){
 const router=useRouter(),{registers}=useRegister(),{can,canAny,loading:permissionsLoading}=useRbac();
 const viewRegisters=can('register:view'),viewIntake=can('intakeSubmission:view'),editIntake=can('intakeSubmission:edit'),viewChanges=can('changeRequest:view'),viewTasks=canAny(['verificationIntakeForm:create','verificationChangeRequest:create']);
 const [intakeType,setIntakeType]=useState('household'),[searchType,setSearchType]=useState('household'),[query,setQuery]=useState('');
 const household=registers.find(r=>r.register_mnemonic.toLowerCase()==='household'),intakeRegister=registers.find(r=>r.register_mnemonic.toLowerCase()===intakeType);
 const {forms}=useIntakeForms(household?.register_id);const form=forms.find(f=>f.form_id==='c1000000-0000-4000-8000-000000000002')||forms[0];
 const recordStats=useFetch<any[]>({url:'/api/stats/register',enabled:!permissionsLoading&&viewRegisters});
 const changes=useFetch<any>({url:'/api/stats/change-request',enabled:!permissionsLoading&&viewChanges});
 const tasks=useFetch<any>({url:'/api/stats/tasks',enabled:!permissionsLoading&&viewTasks});
 const intakeOptions=(status:string)=>({method:'POST',body:JSON.stringify({register_id:intakeRegister?.register_id,current_page:1,page_size:1,filter_by:status==='all'?'':JSON.stringify({workflow_status:status}),search_text:''})});
 const intakeReady=!permissionsLoading&&viewIntake&&!!intakeRegister;
 const pending=useFetch<any>({url:'/api/intake-form/search-in-intake-form-submission',enabled:intakeReady,options:intakeOptions('pending')});
 const drafts=useFetch<any>({url:'/api/intake-form/search-in-intake-form-submission',enabled:intakeReady,options:intakeOptions('draft')});
 const totalForms=useFetch<any>({url:'/api/intake-form/search-in-intake-form-submission',enabled:intakeReady,options:intakeOptions('all')});
 const count=(type:string)=>Array.isArray(recordStats.data)?recordStats.data.find(r=>r.register_id===registers.find(r=>r.register_mnemonic.toLowerCase()===type)?.register_id)?.total_record_count:undefined;
 const failure=(result:{data:any;error:string|null})=>!!result.error||!!result.data?.error;
 const value=(result:{data:any})=>result.data?.pagination?.number_of_items;
 return <>
  <section className={styles.hero} aria-labelledby="registration-title"><div className={styles.heroCopy}><span className={styles.eyebrow}>ONE REGISTRY. EVERY HOUSEHOLD.</span><h1 id="registration-title">Register your household</h1><p>Capture household members, location and living conditions. Follow every registration from first entry to independent approval.</p><div className={styles.actions}><Action href={form?'/intake-form/household/new/'+form.form_id:'/intake-form/household'} allowed={editIntake&&!!form} icon="home" primary>Register your household</Action><Action href="/intake-form/household" allowed={viewIntake} icon="form">View submissions</Action></div></div><div className={styles.heroGraphic} aria-hidden="true"><div className={styles.orbit}/><div className={styles.graphicHome}><Icon name="home"/></div><div className={styles.graphicPeople}><Icon name="people"/></div><div className={styles.graphicCheck}><Icon name="task"/></div><span>Capture → Review → Publish</span></div></section>
  <div className={styles.quickActions}><span className={styles.quickLabel}>Your registry tools</span><div><Action href="/configuration/registry/users" allowed={can('registryConfiguration:edit')} icon="staff">Staff and roles</Action><Action href="/offline" allowed={editIntake} icon="offline">Offline field capture</Action></div></div>
  <form className={styles.search} onSubmit={e=>{e.preventDefault();router.push('/register/'+searchType+(query.trim()?'?search='+encodeURIComponent(query.trim())+'&page=1':''))}} role="search" aria-label="Search master registry"><Icon name="search"/><label className={styles.srOnly} htmlFor="dashboard-register">Registry</label><select id="dashboard-register" value={searchType} onChange={e=>setSearchType(e.target.value)}><option value="household">Households</option><option value="individual">Individuals</option></select><label className={styles.srOnly} htmlFor="dashboard-search">Name or record ID</label><input id="dashboard-search" value={query} onChange={e=>setQuery(e.target.value)} placeholder="Search by name or record ID" disabled={!viewRegisters}/><button type="submit" disabled={!viewRegisters}>Search<Icon name="arrow"/></button></form>
  <div className={styles.grid}>
   {viewRegisters&&<Panel id="registry-title" title="Master Registry" subtitle="Published records, ready to use" icon="home" tag="LIVE RECORDS" tone="registry"><div className={styles.metrics}><Metric label="Households" value={count('household')} href="/register/household" icon="home" allowed={viewRegisters} loading={recordStats.loading} failed={failure(recordStats)}/><Metric label="Individuals" value={count('individual')} href="/register/individual" icon="people" allowed={viewRegisters} loading={recordStats.loading} failed={failure(recordStats)}/></div></Panel>}
   {viewIntake&&<Panel id="forms-title" title="Form submissions" subtitle={`${intakeType==='household'?'Household':'Individual'} registration progress`} icon="form" tag={intakeReady&&!totalForms.loading&&!failure(totalForms)?`${value(totalForms)??0} TOTAL`:'REGISTRATION'}><div className={styles.segment} role="group" aria-label="Submission registry">{['household','individual'].map(type=><button key={type} type="button" aria-pressed={intakeType===type} onClick={()=>setIntakeType(type)}>{type==='household'?'Households':'Individuals'}</button>)}</div><div className={styles.metrics}><Metric label="Pending submissions" value={value(pending)} href={'/intake-form/'+intakeType+'?status=pending'} icon="task" allowed={viewIntake} loading={pending.loading||!intakeReady} failed={failure(pending)}/><Metric label="Draft submissions" value={value(drafts)} href={'/intake-form/'+intakeType+'?status=draft'} icon="form" allowed={viewIntake} loading={drafts.loading||!intakeReady} failed={failure(drafts)}/></div></Panel>}
   {viewChanges&&<Panel id="changes-title" title="Change requests" subtitle="Updates to published records" icon="change" tag="RECORD UPDATES"><div className={styles.metrics}><Metric label="Approved changes" value={changes.data?.approved_count} href="/change-request?status=approved" icon="task" allowed={viewChanges} loading={changes.loading} failed={failure(changes)}/><Metric label="Pending changes" value={changes.data?.pending_count} href="/change-request?status=pending" icon="change" allowed={viewChanges} loading={changes.loading} failed={failure(changes)}/></div></Panel>}
   {viewTasks&&<Panel id="tasks-title" title="My tasks" subtitle="Your assigned approval queues" icon="task" tag="ACTION CENTRE" tone="tasks"><div className={styles.metrics}><Metric label="Registration reviews" value={tasks.data?.intake_form_count} href="/tasks/intake-form?status=pending" icon="form" allowed={viewTasks} loading={tasks.loading} failed={failure(tasks)}/><Metric label="Change request reviews" value={tasks.data?.change_request_count} href="/tasks/change-request?status=pending" icon="change" allowed={viewTasks} loading={tasks.loading} failed={failure(tasks)}/></div></Panel>}
  </div>
  <div className={styles.journey} aria-label="Registration workflow"><strong>From capture to master record</strong><ol>{['Capture & save','Submit for review','Approval level 1','Approval level 2','Publish to registry'].map((step,i)=><li key={step}><span>{i+1}</span>{step}</li>)}</ol></div>
 </>;
}
export default function Home(){const [version,setVersion]=useState(0);return <main className={styles.dashboard}><div className={styles.shell}><div className={styles.heading}><div><span className={styles.eyebrow}>MASTER BENEFICIARY REGISTRY</span><h2>Registry overview</h2></div><button type="button" onClick={()=>setVersion(v=>v+1)} className={styles.refresh} aria-label="Refresh dashboard"><Icon name="refresh"/>Refresh dashboard</button></div><Dashboard key={version}/><p className={styles.footnote} role="status" aria-live="polite">{version?'Dashboard refreshed. ':''}Counts reflect the records and queues available to your account.</p></div></main>}
