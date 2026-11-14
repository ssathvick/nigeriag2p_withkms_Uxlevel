import names from './record-names.json';
import {programmeName} from './programme-names';
export const readable = v => typeof v==='string' ? programmeName(v).replace(/_/g,' ') : v;
export function recordName(model,id,raw){const known=names[model]?.[id];return known&&known.raw===raw?known.name:readable(raw);}
export function namedValue(model,key,value,row,field){
 if(field?.type==='many2one'&&Array.isArray(value))return recordName(field.relation,value[0],value[1]);
 if(key==='display_name'||key==='name'||key==='mnemonic'||key.endsWith('_mnemonic'))return recordName(model,row?.id,value);
 if(key==='cycle_number')return `Enrollment cycle ${value}`;
 if(field?.type==='selection')return readable(field.selection?.find(x=>x[0]===value)?.[1]||value);
 return value;
}
export function fieldLabel(key,f={},editing=false){
 const labels={nsipa_status:'List approval',nsipa_approval_status:'List approval',nsipa_enrollment_cycle_id:'Approved enrolment cycle',nsipa_flow:'Programme approval flow',nsipa_setup_ready:'Programme setup complete',nsipa_revision:'List revision',nsipa_total:'Total entitlement NGN',nsipa_error:'Processing error',program_id:'Programme',benefit_code_id:'Benefit',enrollment_cycle_id:'Enrollment cycle',disbursement_cycle_id:'Disbursement cycle',cycle_number:'Enrollment cycle',mnemonic:'Name',program_mnemonic:'Programme name',cycle_mnemonic:'Disbursement cycle name',benefit_mnemonic:'Benefit name',agency_mnemonic:'Agency name',warehouse_mnemonic:'Warehouse or bank name',area_mnemonic:'Area name',display_name:'Name',pbms_domain:'Eligibility filter (advanced)',set_operator:'Rule combination',list_stage:'Processing stage',list_workflow_status:'Approval status',eligibility_process_status:'Eligibility calculation',entitlement_process_status:'Benefit calculation',envelope_creation_status:'Payment envelope preparation',disbursement_batch_creation_status:'Payment batch preparation'};
 if(editing&&(key==='mnemonic'||key.endsWith('_mnemonic')))return (labels[key]||'Name').replace(/name$/i,'code')+' (system reference)';
 return labels[key]||readable(f.string||key);
}
export function matchingIds(model,q){return Object.entries(names[model]||{}).filter(([,r])=>r.name.toLowerCase().includes(q.toLowerCase())).map(([id])=>Number(id));}
export function workflowName(raw){for(const model of ['g2p.beneficiary.list','g2p.benefit.codes']){const entry=Object.values(names[model]||{}).find(r=>r.raw===raw);if(entry)return entry.name;}return readable(raw);}
