'use client';
import {useState} from 'react';
import {usePathname,useRouter,useSearchParams} from 'next/navigation';
import {Eye,EyeOff,Copy,Info} from 'lucide-react';

export function InfoHint({text}:{text:string}) {
 return <span className="relative inline-flex group align-middle ml-2"><span tabIndex={0} role="img" aria-label={text} className="rounded-full p-1 focus-visible:outline-2"><Info size={16}/></span><span role="tooltip" className="pointer-events-none absolute z-50 left-0 top-full hidden group-hover:block group-focus-within:block w-64 max-w-[75vw] rounded-lg bg-neutral-first text-white p-3 text-sm font-normal whitespace-normal shadow-lg">{text}</span></span>;
}
export function WorkflowStatus({approval,draft,summary}:{approval?:string;draft?:string;summary?:string|null}) {
 const status=summary?.startsWith('returned')?'Returned for correction':approval==='REJECTED'?'Rejected':draft==='DRAFT'?'Draft':approval==='APPROVED'?'Approved':'Pending';
 const color=status==='Approved'?'bg-green-100 text-green-900':status==='Rejected'?'bg-red-100 text-red-900':status==='Draft'?'bg-slate-100 text-slate-700':'bg-amber-100 text-amber-900';
 return <span className={`inline-flex items-center gap-2 rounded-full px-4 py-1 text-sm font-semibold whitespace-nowrap ${color}`}><span aria-hidden="true" className="h-2 w-2 rounded-full bg-current"/>{status}</span>;
}
export function PrivateIdentifier({value}:{value?:string|null}) {
 const [visible,setVisible]=useState(false);const [copied,setCopied]=useState(false);
 if(!value)return <span>Not recorded</span>;
 return <span className="inline-flex flex-wrap items-center gap-2 text-sm break-all"><span>{visible?value:'•••'+value.slice(-3)}</span><button type="button" aria-label={visible?'Hide identifier':'Show full identifier'} onClick={e=>{e.preventDefault();e.stopPropagation();setVisible(!visible)}} className="p-1 rounded-full hover:bg-secondary-second">{visible?<EyeOff size={16}/>:<Eye size={16}/>}</button><button type="button" aria-label="Copy identifier" onClick={async e=>{e.preventDefault();e.stopPropagation();await navigator.clipboard.writeText(value);setCopied(true);setTimeout(()=>setCopied(false),1800)}} className="p-1 rounded-full hover:bg-secondary-second"><Copy size={16}/></button>{copied&&<span role="status">Copied</span>}</span>;
}
export function WorkflowFilters({draft=false,tasks=false}:{draft?:boolean;tasks?:boolean}) {
 const router=useRouter(),path=usePathname(),query=useSearchParams();const selected=query.get('status')||'all';
 const items=[['all','All'],...(draft?[['draft','Draft']]:[]),['pending','Pending'],[tasks?'completed':'approved','Completed'],['returned','Returned'],['rejected','Rejected']];
 return <nav aria-label="Filter by status" className="flex flex-wrap gap-2 px-7.5 py-4">{items.map(([value,label])=><button key={value} type="button" aria-pressed={selected===value} onClick={()=>{const p=new URLSearchParams(query.toString());p.set('status',value);p.set('page','1');router.push(path+'?'+p)}} className={`rounded-full px-5 py-2 font-medium text-sm transition-colors ${selected===value?'bg-neutral-first text-white':'bg-white text-neutral-first hover:bg-primary-first'}`}>{label}</button>)}</nav>;
}
