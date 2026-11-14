'use client';
import {Link} from '@/i18n/navigation';
import {useRbac} from '@/context/RbacContext';
import {Settings2,Database,ArrowDownToLine,ArrowUpFromLine,ShieldCheck} from 'lucide-react';
import {configurationSections} from './configurationAccess';
export default function ConfigSidebar({activeOption}:{activeOption:string}){
 const {can}=useRbac();const visible=configurationSections.filter(s=>can(s.access.view));const groups=[...new Set(visible.map(s=>s.group))];
 const icons:Record<string,any>={'Registry':Settings2,'Data and registration':Database,'Incoming data':ArrowDownToLine,'Outgoing data':ArrowUpFromLine,'Governance':ShieldCheck};
 return <nav aria-label="Configuration sections">{groups.map(group=>{const Icon=icons[group];return <section key={group} className="configuration-nav-group"><h2><Icon size={16}/>{group}</h2>{visible.filter(s=>s.group===group).map(s=><Link key={s.id} href={s.path} aria-current={activeOption===s.id?'page':undefined}>{s.title}<span aria-hidden="true">↗</span></Link>)}</section>})}</nav>;
}
