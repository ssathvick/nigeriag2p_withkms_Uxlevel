'use client';
import {useAuth} from '@/context/Authcontext';
export function useRegistryScope(){return useAuth().user?.registry_scope as string|undefined;}
export default function RegistryScope(){
 const scope=useRegistryScope();
 const descriptions:Record<string,string>={
  field:'Your records only. After Level 1 approval, the record leaves your workspace. A revalidation request returns it to you for correction and resubmission.',
  level1:'Level 1 review: field-agent submissions awaiting your decision. Approval sends the record to Level 2; revalidation returns it to its creator.',
  level2:'Level 2 review: field-agent submissions approved at Level 1. Approval publishes the record for MBR Officer; revalidation returns it to its creator.',
  officer:'MBR Officer: read-only access to field-agent records approved at both levels.',
  admin:'MBR Admin: access to all records, including permanently rejected records in the rejected archive.'
 };
 if(!scope||!descriptions[scope])return null;
 return <aside role="note" style={{maxWidth:1440,margin:'16px auto',padding:'14px 24px',borderLeft:'4px solid #155e50',background:'#edf5f0',color:'#164b41',fontSize:14}}>{descriptions[scope]}</aside>;
}
