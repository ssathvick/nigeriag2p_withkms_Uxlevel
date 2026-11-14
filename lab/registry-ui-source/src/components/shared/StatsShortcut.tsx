'use client';
import {useRouter} from '@/i18n/navigation';
import {useRegister} from '@/context/RegisterContext';
export function useStatsShortcut(endpoint:string){
 const router=useRouter(),{registers}=useRegister();
 return (id?:string)=>{
  if(endpoint.includes('register')){
   const item=registers.find(r=>r.register_id===id)||registers.find(r=>r.register_mnemonic.toLowerCase()==='household')||registers[0];
   if(item)router.push('/register/'+item.register_mnemonic.toLowerCase());
  }else if(endpoint.includes('intake'))router.push('/intake-form/household'+(id==='pendingSubmissions'?'?status=pending':id==='draftSubmissions'?'?status=draft':''));
  else if(endpoint.includes('change'))router.push('/change-request'+(id?'?status='+id:''));
  else if(endpoint.includes('tasks'))router.push((id==='intake_form'?'/tasks/intake-form':'/tasks/change-request')+'?status=pending');
  else if(endpoint.includes('messages'))router.push(id==='outgoingMessages'?'/outgoing-messages':'/incoming-messages');
 };
}
