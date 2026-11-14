'use client';
import {useState} from 'react';
import {useBaseWidget,widgetRegistry,type BaseWidgetConfig} from '@openg2p/registry-widgets';
import {useFetch} from '@/shared/hooks/useFetch';
import type {RegisterRecordsApiResponse} from '@/features/register/types';

/** Published-household selector for the individual registration and section editor. */
function HouseholdLookupWidget({config}:{config:BaseWidgetConfig}){
 const {value,onChange,isEnabled}=useBaseWidget({config});
 const [query,setQuery]=useState(''),[search,setSearch]=useState(''),[page,setPage]=useState(1),[open,setOpen]=useState(false),[selectedName,setSelectedName]=useState('');
 const registerId='a0000000-0000-4000-8000-000000000002';
 const {data,loading,error}=useFetch<RegisterRecordsApiResponse>({url:'/api/register/records',enabled:open,options:{method:'POST',body:JSON.stringify({register_id:registerId,current_page:page,page_size:10,sort_by:'',filter_by:{},search_text:search})}});
 const {data:linked}=useFetch<any[]>({url:'/api/register/tab-sections-data',enabled:!!value,options:{method:'POST',body:JSON.stringify({register_id:registerId,internal_record_id:value,tab_id:'household_info_tab'})}});
 const name=selectedName||(Array.isArray(linked)?linked:[]).flatMap(s=>s.records||[]).find(r=>r.internal_record_id===value)?.record_name;
 const readonly=!!config['widget-readonly'];
 return <div className="min-w-0 rounded-xl border border-primary-second p-4" data-widget-id={config['widget-id']}>
  <p className="mb-2 font-semibold">Linked household{config['widget-required']?' *':''}</p>
  {value?<p className="mb-3 break-words">{name||'Household reference'}<span className="block text-sm text-secondary-third">{String(value)}</span></p>:<p className="mb-3 text-sm">{readonly?'No household linked.':'Select the household this individual belongs to.'}</p>}
  {!readonly&&<button type="button" disabled={!isEnabled} onClick={()=>setOpen(!open)} aria-expanded={open} className="rounded-full border px-4 py-2">{open?'Close household search':value?'Change linked household':'Find household'}</button>}
  {open&&!readonly&&<div className="mt-4 space-y-3">
   <label className="flex flex-col gap-2 text-sm">Household name or ID<input value={query} onChange={e=>setQuery(e.target.value)} onKeyDown={e=>{if(e.key==='Enter'){e.preventDefault();setSearch(query.trim());setPage(1)}}} className="min-w-0 rounded-lg border px-3 py-2"/></label>
   <button type="button" disabled={loading} onClick={()=>{setSearch(query.trim());setPage(1)}} className="rounded-full bg-neutral-first px-4 py-2 text-white">Search households</button>
   {loading?<p role="status">Loading households…</p>:error||data&&'error' in data?<p role="alert">Households could not load. Try searching again.</p>:<ul className="space-y-2">{data?.records?.map(r=><li key={r.internal_record_id}><button type="button" className="w-full rounded-lg border p-3 text-left whitespace-normal break-words" onClick={()=>{onChange(r.internal_record_id);setSelectedName(r.record_name);setOpen(false)}}><strong className="block">{r.record_name}</strong><span className="text-sm">{r.functional_record_id||r.internal_record_id}</span></button></li>)}{data?.records?.length===0&&<li>No matching households found.</li>}</ul>}
   <div className="flex flex-wrap items-center gap-3"><button type="button" disabled={loading||page===1} onClick={()=>setPage(p=>p-1)} className="rounded-full border px-3 py-2">Previous households</button><span>Page {page}</span><button type="button" disabled={loading||page>=(data?.pagination?.number_of_pages||1)} onClick={()=>setPage(p=>p+1)} className="rounded-full border px-3 py-2">Next households</button></div>
  </div>}
 </div>;
}
widgetRegistry.register({widget:'register-lookup',component:HouseholdLookupWidget});
export default HouseholdLookupWidget;
