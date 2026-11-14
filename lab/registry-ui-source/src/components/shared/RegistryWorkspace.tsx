'use client';
import {type ReactNode} from 'react';
import {Link,usePathname} from '@/i18n/navigation';
import {useRbac} from '@/context/RbacContext';
import {useRegister} from '@/context/RegisterContext';
import {useFetch} from '@/shared/hooks/useFetch';
import {useIntakeForms} from '@/features/intake-form/hooks/useIntakeForms';
import './registry-workspace.css';

function WorkspaceIcon({kind}:{kind:string}){
 const path=kind==='register'?'m3 10 9-7 9 7v10H3ZM9 21v-8h6v8':kind==='tasks'?'M5 5h14v16H5ZM9 5V3h6v2M8 13l3 3 5-6':kind==='change-request'?'M20 8A8 8 0 0 0 6 5L3 8m0-5v5h5M4 16a8 8 0 0 0 14 3l3-3m0 5v-5h-5':'M14 3H5v18h14V8ZM14 3v5h5M8 12h8M8 16h5';
 return <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d={path}/></svg>;
}
function QueueTile({href,label,value,loading,error,kind}:{href:string;label:string;value:any;loading:boolean;error:boolean;kind:string}){
 return <Link href={href} className="workspace-queue" aria-label={`${label}: ${loading?'Loading':error?'Unavailable':value??0}`} aria-busy={loading}><WorkspaceIcon kind={kind}/><span><strong>{loading?'…':error?'Unavailable':new Intl.NumberFormat('en-NG').format(Number(value??0))}</strong><span>{label}</span></span><span className="workspace-arrow" aria-hidden="true">↗</span></Link>;
}
function Workspace({children,path}:{children:ReactNode;path:string}){
 const {can,canAny,loading}=useRbac(),{registers}=useRegister();
 const parts=path.split('/').filter(Boolean),kind=parts[0],recordType=kind==='tasks'&&parts[1]==='intake-form'?parts[2]:parts[1],type=recordType==='individual'?'individual':'household';
 const isCollection=['change-request','incoming-messages','outgoing-messages'].includes(kind)?parts.length===1:parts.length===2;
 const isNew=parts.includes('new'),isHistory=parts.includes('version-history');
 const viewRegisters=can('register:view'),viewIntake=can('intakeSubmission:view'),viewChanges=can('changeRequest:view'),review=canAny(['verificationIntakeForm:create','verificationChangeRequest:create']);
 const register=registers.find(r=>r.register_mnemonic.toLowerCase()===type),{forms}=useIntakeForms(can('intakeSubmission:edit')&&['register','intake-form'].includes(kind)?register?.register_id:undefined);
 const form=forms.find(f=>f.register_id===register?.register_id)||forms[0];
 const recordStats=useFetch<any>({url:'/api/stats/register',enabled:isCollection&&!loading&&viewRegisters&&kind==='register'});
 const changes=useFetch<any>({url:'/api/stats/change-request',enabled:isCollection&&!loading&&viewChanges&&kind==='change-request'});
 const tasks=useFetch<any>({url:'/api/stats/tasks',enabled:isCollection&&!loading&&review&&kind==='tasks'});
 const intake=(status:string)=>({method:'POST',body:JSON.stringify({register_id:register?.register_id,current_page:1,page_size:1,filter_by:JSON.stringify({workflow_status:status}),search_text:''})});
 const intakeReady=isCollection&&!loading&&viewIntake&&!!register&&['register','intake-form'].includes(kind);
 const pending=useFetch<any>({url:'/api/intake-form/search-in-intake-form-submission',enabled:intakeReady,options:intake('pending')});
 const drafts=useFetch<any>({url:'/api/intake-form/search-in-intake-form-submission',enabled:intakeReady,options:intake('draft')});
 const labels:Record<string,string>={register:type==='household'?'Household registry':'Individual registry','intake-form':'Registration review',tasks:'Approval workspace','change-request':'Change requests','incoming-messages':'Incoming messages','outgoing-messages':'Outgoing messages'};
 const title=isHistory?'Record version history':isNew?`Register ${type==='household'?'your household':'an individual'}`:labels[kind];
 const descriptions:Record<string,string>={register:'Explore published records and manage approved updates in one place.','intake-form':'Track drafts, review registrations and follow every correction through to publication.',tasks:'Review your assigned records with clear decisions and a complete approval history.','change-request':'Compare proposed updates, follow their review and protect the published master record.','incoming-messages':'Follow received records through validation, transformation and registry processing.','outgoing-messages':'Track records shared from the registry and the topics resolved for delivery.'};
 const nav=[{href:'/register/household',label:'Households',allowed:viewRegisters},{href:'/register/individual',label:'Individuals',allowed:viewRegisters},{href:'/intake-form/'+type,label:'Registration review',allowed:viewIntake},{href:'/tasks/intake-form',label:'Approvals',allowed:review},{href:'/change-request',label:'Change requests',allowed:viewChanges},{href:'/incoming-messages',label:'Incoming messages',allowed:can('incomingMessage:view')},{href:'/outgoing-messages',label:'Outgoing messages',allowed:can('outgoingMessage:view')}];
 const failed=(r:{data:any;error:string|null})=>!!r.error||!!r.data?.error;
 return <div className="registry-workspace" data-workspace-kind={kind} data-workspace-type={type}>
  <div className="workspace-shell"><header className="workspace-header"><div className="workspace-heading"><span className="workspace-icon"><WorkspaceIcon kind={kind}/></span><div><span className="workspace-eyebrow">MASTER BENEFICIARY REGISTRY</span><h1>{title}</h1><p>{descriptions[kind]}</p></div></div><div className="workspace-actions"><Link href="/" className="workspace-button workspace-back">← Dashboard</Link>{!isNew&&can('intakeSubmission:edit')&&form&&['register','intake-form'].includes(kind)&&<Link className="workspace-button workspace-primary" href={`/intake-form/${type}/new/${form.form_id}`}>+ Register {type==='household'?'household':'individual'}</Link>}</div></header>
  <nav className="workspace-nav" aria-label="Registry workspace">{nav.filter(n=>n.allowed).map(n=><Link key={n.href} href={n.href} aria-current={(n.label==='Approvals'?kind==='tasks':n.href===path||path.startsWith(n.href+'/'))?'page':undefined}>{n.label}</Link>)}</nav>
  {isCollection&&<div className="workspace-queues" aria-label="Registry queue overview">
   {kind==='register'&&viewRegisters&&<QueueTile href={'/register/'+type} label={type==='household'?'Published households':'Published individuals'} value={Array.isArray(recordStats.data)?recordStats.data.find((r:any)=>r.register_id===register?.register_id)?.total_record_count:0} loading={recordStats.loading} error={failed(recordStats)} kind="register"/>}
   {intakeReady&&<><QueueTile href={`/intake-form/${type}?status=pending`} label="Pending registrations" value={pending.data?.pagination?.number_of_items} loading={pending.loading} error={failed(pending)} kind="tasks"/><QueueTile href={`/intake-form/${type}?status=draft`} label="Draft registrations" value={drafts.data?.pagination?.number_of_items} loading={drafts.loading} error={failed(drafts)} kind="intake-form"/></>}
   {kind==='change-request'&&viewChanges&&<><QueueTile href="/change-request?status=approved" label="Approved changes" value={changes.data?.approved_count} loading={changes.loading} error={failed(changes)} kind="tasks"/><QueueTile href="/change-request?status=pending" label="Pending changes" value={changes.data?.pending_count} loading={changes.loading} error={failed(changes)} kind="change-request"/></>}
   {kind==='tasks'&&review&&<><QueueTile href="/tasks/intake-form?status=pending" label="My registration reviews" value={tasks.data?.intake_form_count} loading={tasks.loading} error={failed(tasks)} kind="intake-form"/><QueueTile href="/tasks/change-request?status=pending" label="My change request reviews" value={tasks.data?.change_request_count} loading={tasks.loading} error={failed(tasks)} kind="change-request"/></>}
  </div>}
  <div className="workspace-content">{children}</div></div>
 </div>;
}
export default function RegistryWorkspace({children}:{children:ReactNode}){
 const path=usePathname();
 const active=/^\/(?:register\/(?:household|individual)|intake-form\/(?:household|individual)|tasks\/(?:intake-form|change-request)|change-request|incoming-messages|outgoing-messages)(?:\/|$)/.test(path);
 return active?<Workspace path={path}>{children}</Workspace>:<>{children}</>;
}
