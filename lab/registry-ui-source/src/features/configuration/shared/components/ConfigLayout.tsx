'use client';

import ConfigSidebar from './ConfigSidebar';
import { ReactNode,useState,useEffect } from 'react';
import {Link,usePathname} from '@/i18n/navigation';
import {useRbac} from '@/context/RbacContext';
import {Settings2,Menu,ChevronDown} from 'lucide-react';
import {ConfigurationAccessContext,sectionForPath} from './configurationAccess';
import './configuration-workspace.css';

export type ConfigActiveOption =
    | "registry"
    | "registry-details"
    | "registry-themes"
    | "registry-languages"
    | "registers"
    | "intake-forms"
    | "data-models"
    | "ingest-configurations"
    | "outgest-configurations"
    | "ingest-key-paths"
    | "ingest-semantic-patterns"
    | "ingest-manage-subscription"
    | "ingest-templates"
    | "outgest-topics"
    | "outgest-templates"
    | "data-policies"
    | "awe-policy-config"

interface ConfigLayoutProps {
    children: ReactNode;
    activeOption: ConfigActiveOption;
}

export const ConfigLayout = ({ children, activeOption }: ConfigLayoutProps) => {
 const [menuOpen,setMenuOpen]=useState(false),path=usePathname();const {can}=useRbac();
 useEffect(()=>setMenuOpen(false),[path]);
 const section=sectionForPath(path),isDetail=path!==section.path;
 return <ConfigurationAccessContext.Provider value={section.access}><main className="registry-workspace configuration-workspace"><div className="workspace-shell"><header className="workspace-header"><div className="workspace-heading"><span className="workspace-icon"><Settings2 size={28}/></span><div><span className="workspace-eyebrow">MASTER BENEFICIARY REGISTRY · CONFIGURATION</span><h1>{section.title}</h1><p>{section.description}</p></div></div><div className="workspace-actions"><Link href="/" className="workspace-button">← Dashboard</Link>{can('registryConfiguration:edit')&&<Link href="/configuration/registry/users" className="workspace-button workspace-primary">Staff and roles</Link>}</div></header><div className="configuration-frame"><aside className="configuration-navigation"><button type="button" className="configuration-menu-toggle" aria-expanded={menuOpen} aria-controls="configuration-section-menu" onClick={()=>setMenuOpen(!menuOpen)}><Menu size={19}/><span>Configuration sections</span><ChevronDown size={17}/></button><div id="configuration-section-menu" className={menuOpen?'configuration-menu is-open':'configuration-menu'}><ConfigSidebar activeOption={activeOption}/></div></aside><div className="configuration-content workspace-content" data-config-detail={isDetail}>{children}</div></div></div></main></ConfigurationAccessContext.Provider>;
};
export default ConfigLayout;
