'use client';
import {Link} from '@/i18n/navigation';
import {ShieldCheck,SearchX,RefreshCw} from 'lucide-react';
export default function ApplicationState({kind,title,description,onRetry}:{kind:'forbidden'|'not-found'|'error';title:string;description:string;onRetry?:()=>void}){
 const Icon=kind==='forbidden'?ShieldCheck:kind==='not-found'?SearchX:RefreshCw;
 return <main className="application-state"><section><span className="application-state-icon"><Icon size={38}/></span><span className="workspace-eyebrow">MASTER BENEFICIARY REGISTRY</span><h1>{title}</h1><p>{description}</p><div>{onRetry&&<button type="button" onClick={onRetry}>Try again</button>}<Link href="/">Return to dashboard</Link></div></section></main>;
}
