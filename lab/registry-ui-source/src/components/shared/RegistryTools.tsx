'use client';
import {type ReactNode} from 'react';
import {Link} from '@/i18n/navigation';
import {useRbac} from '@/context/RbacContext';
import './registry-tools.css';

export function ToolIcon({kind}:{kind:'staff'|'offline'|'check'|'users'|'shield'|'arrow'}){
 const path={staff:'M9 10a3 3 0 1 0 0-6 3 3 0 0 0 0 6ZM3 21v-3a6 6 0 0 1 10-4M18 11l4 2v3c0 3-4 5-4 5s-4-2-4-5v-3Z',offline:'M8 2h8a1 1 0 0 1 1 1v18a1 1 0 0 1-1 1H8a1 1 0 0 1-1-1V3a1 1 0 0 1 1-1ZM9 12l2 2 4-4M10 18h4',check:'M20 6 9 17l-5-5',users:'M9 10a3 3 0 1 0 0-6 3 3 0 0 0 0 6ZM3 21v-3a6 6 0 0 1 12 0v3M17 5a3 3 0 0 1 0 6M17 15a5 5 0 0 1 4 5',shield:'m12 3 8 4v5c0 6-8 9-8 9s-8-3-8-9V7ZM8 12l3 3 5-6',arrow:'M5 12h14m-5-5 5 5-5 5'}[kind];
 return <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d={path}/></svg>;
}
export function RegistryTools({kind,title,description,children}:{kind:'staff'|'offline';title:string;description:string;children:ReactNode}){
 const {can}=useRbac();
 return <main className="registry-workspace registry-tools"><div className="workspace-shell"><header className="workspace-header"><div className="workspace-heading"><span className="workspace-icon"><ToolIcon kind={kind}/></span><div><span className="workspace-eyebrow">MASTER BENEFICIARY REGISTRY</span><h1>{title}</h1><p>{description}</p></div></div><Link href="/" className="workspace-button workspace-back">← Dashboard</Link></header><nav className="workspace-nav" aria-label="Registry tools"><Link href="/">Registry overview</Link>{can('register:view')&&<Link href="/register/household">Master Registry</Link>}{can('registryConfiguration:edit')&&<Link href="/configuration/registry/users" aria-current={kind==='staff'?'page':undefined}>Staff and roles</Link>}{can('intakeSubmission:edit')&&<Link href="/offline" aria-current={kind==='offline'?'page':undefined}>Offline field capture</Link>}</nav>{children}</div></main>;
}
