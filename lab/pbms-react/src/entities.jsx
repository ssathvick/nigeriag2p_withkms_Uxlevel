import React,{useEffect,useState}from'react';
import{call}from'./api';

export const editable={
 'g2p.enrollment.cycle':['program_id','cycle_number','enrollment_start_date','enrollment_end_date','disbursement_start_date','disbursement_end_date'],
 'g2p.disbursement.cycle':['program_id','cycle_mnemonic','disbursement_schedule_date'],
 'g2p.beneficiary.list':['mnemonic','brief','enrollment_cycle_id','disbursement_cycle_id'],
 'g2p.eligibility.rule.definition':['program_id','rule_number','mnemonic','description','target_registry','set_operator','pbms_domain'],
 'g2p.entitlement.rule.definition':['program_id','mnemonic','description','target_registry','benefit_code_id','quantity','multiplier','pbms_domain'],
 'g2p.priority.rule.definition':['disbursement_cycle_id','mnemonic','description','target_registry','pbms_domain'],
 'g2p.benefit.codes':['benefit_mnemonic','benefit_type','benefit_description','decimal_places','measurement_unit'],
 'g2p.program.benefit.codes':['program_id','benefit_code_id','max_quantity'],
 'g2p.agency':['name','agency_mnemonic','admin_name','admin_email','admin_mobile','administrative_area_small_ids'],
 'g2p.warehouse':['name','warehouse_mnemonic','is_sponsor_bank','admin_name','admin_email','admin_mobile','administrative_area_large_ids'],
 'g2p.agency.program.benefit.codes':['agency_id','program_id','benefit_code_id','additional_info'],
 'g2p.warehouse.program.benefit.codes':['warehouse_id','program_id','benefit_code_id','additional_info'],
 'g2p.administrative.area.large':['area_mnemonic','area_description'],
 'g2p.administrative.area.small':['area_mnemonic','area_description','administrative_area_large_id'],
};
for(const kind of ['farmer','household','student'])editable[`g2p.${kind}.registry`]=['link_registry_id','name','gender',...(kind==='farmer'?['land_area','no_of_cattle_heads','no_of_poultry_heads','annual_income']:kind==='household'?['size_total','size_adults','size_children','annual_income']:['institution_name','date_of_birth']),'large_area_id','large_area_code','small_area_id','small_area_code'];
const groupMap={enrollment:'group_enrolment_editor',disbursement:'group_disbursement_editor',lists:'group_beneficiary_list_editor',eligibility:'group_program_editor',entitlements:'group_program_editor',priority:'group_priority_rules_editor',benefits:'group_benefit_code_editor','programme-benefits':'group_program_editor',agencies:'group_agency_editor',warehouses:'group_warehouse_editor','agency-benefits':'group_benefit_code_editor','warehouse-benefits':'group_warehouse_editor',states:'group_geography_editor',lgas:'group_geography_editor'};
export async function editGroup(item){return groupMap[item.key]?call('res.users','has_group',['g2p_pbms.'+groupMap[item.key]]):true;}
const scalar=(v,f)=>f.type==='many2one'?(Array.isArray(v)?v[0]:v||false):v;
export function RelationInput({field,value,onChange,disabled,domain=[]}){
 const[q,setQ]=useState(''),[options,setOptions]=useState([]),[error,setError]=useState('');
 useEffect(()=>{let live=true;const timer=setTimeout(()=>{call(field.relation,'name_search',[],{name:q,args:domain,operator:'ilike',limit:50}).then(r=>{if(live){setOptions(r);setError('');}}).catch(e=>{if(live)setError(e.message);});},180);return()=>{live=false;clearTimeout(timer);};},[q,field.relation,JSON.stringify(domain)]);
 const multi=field.type==='many2many',id=multi?(value||[]):scalar(value,field);
 return <div className="relation-input"><input aria-label={`Find ${field.string}`} placeholder="Type to find records…" value={q} disabled={disabled} onChange={e=>setQ(e.target.value)}/><select aria-label={field.string} multiple={multi} value={multi?id.map(String):String(id||'')} disabled={disabled} required={field.required} onChange={e=>onChange(multi?[...e.target.selectedOptions].map(o=>Number(o.value)):Number(e.target.value)||false)}>{!multi&&<option value="">Select…</option>}{!multi&&id&&!options.some(([key])=>key===id)&&<option value={id}>{Array.isArray(value)?value[1]:`Record ${id}`}</option>}{multi&&id.filter(key=>!options.some(o=>o[0]===key)).map(key=><option key={key} value={key}>Record {key}</option>)}{options.map(([key,label])=><option key={key} value={key}>{label}</option>)}</select>{error&&<small role="alert">{error}</small>}</div>;
}
export function EntityForm({item,record,defaults={},onClose,onSaved}){
 const[meta,setMeta]=useState(null),[values,setValues]=useState({}),[initial,setInitial]=useState({}),[busy,setBusy]=useState(false),[error,setError]=useState(''),[benefits,setBenefits]=useState(null),[multipliers,setMultipliers]=useState([]);
 const names=editable[item.model]||[];
 useEffect(()=>{if(item.model!=='g2p.entitlement.rule.definition'||!values.target_registry)return;let current=true;call(item.model,'onchange',[[],{target_registry:values.target_registry},['target_registry'],{allowed_multipliers:{}}]).then(r=>{if(current)setMultipliers(JSON.parse(r.value?.allowed_multipliers||'[]'));}).catch(e=>{if(current)setError(e.message);});return()=>{current=false;};},[values.target_registry]);
 const context=Object.fromEntries(Object.entries(defaults).map(([k,v])=>['default_'+k,v]));
 useEffect(()=>{let live=true;(async()=>{try{const m=await call(item.model,'fields_get',[],{attributes:['string','type','relation','required','readonly','selection','help']});const v=record||await call(item.model,'default_get',[names],{context});if(live){setMeta(m);setValues({...v,...(!record?defaults:{})});setInitial(v);}}catch(e){if(live)setError(e.message);}})();return()=>{live=false;};},[]);
 useEffect(()=>{if(!meta||!values.program_id)return;let live=true;const pid=scalar(values.program_id,{type:'many2one'});call('g2p.program.definition','read',[[pid]],{fields:['target_registry','benefit_code_ids']}).then(([p])=>{if(live&&p){setBenefits(p.benefit_code_ids);if(!record&&names.includes('target_registry'))setValues(v=>({...v,target_registry:p.target_registry}));}}).catch(e=>{if(live)setError(e.message);});return()=>{live=false;};},[values.program_id,!!meta]);
 async function submit(e){e.preventDefault();setBusy(true);setError('');try{
  if(record){const keys=['write_date','approved_for_enrollment','approved_for_disbursement','list_workflow_status'].filter(k=>meta[k]);const [fresh]=await call(item.model,'read',[[record.id]],{fields:keys});if(!fresh)throw new Error('This record is no longer available.');if(record.write_date&&fresh.write_date!==record.write_date)throw new Error('This record changed while you were editing. Close and reopen it before saving.');if(fresh.approved_for_enrollment||fresh.approved_for_disbursement||['approved_final_enrolment','approved_for_disbursement'].includes(fresh.list_workflow_status))throw new Error('This workflow is approved and can no longer be edited.');}
  if(names.includes('program_id')&&!values.program_id)throw new Error('Select a programme before saving.');
  if(item.model==='g2p.priority.rule.definition'&&!values.disbursement_cycle_id)throw new Error('Select a disbursement cycle.');
  if(item.model==='g2p.entitlement.rule.definition'&&!values.benefit_code_id)throw new Error('Select a programme benefit.');
  if(item.model==='g2p.beneficiary.list'&&!!values.enrollment_cycle_id===!!values.disbursement_cycle_id)throw new Error('Select exactly one enrollment or disbursement cycle.');
  if(values.enrollment_start_date&&values.enrollment_end_date<values.enrollment_start_date)throw new Error('Enrollment end date must follow the start date.');
  if(values.disbursement_start_date&&values.disbursement_end_date<values.disbursement_start_date)throw new Error('Disbursement end date must follow the start date.');
  const payload={};
  for(const k of names){const f=meta[k];if(!f)continue;let v=scalar(values[k],f);if(v===undefined)continue;
   if(record&&JSON.stringify(v)===JSON.stringify(scalar(initial[k],f)))continue;
   if(record&&['program_id','enrollment_cycle_id','disbursement_cycle_id','cycle_number','decimal_places','is_sponsor_bank'].includes(k))continue;
   if(f.type==='integer'||f.type==='float'){v=Number(v);if(!Number.isFinite(v)||(f.type==='integer'&&!Number.isInteger(v)))throw new Error(`${f.string} needs a valid number.`);}
   if(f.type==='many2many')v=[[6,0,v||[]]];
   payload[k]=v===''?false:v;
  }
  if(names.includes('pbms_domain')){const result=await call(item.model,'onchange',[[],{target_registry:values.target_registry,pbms_domain:values.pbms_domain},['target_registry','pbms_domain'],{sql_query:{}}]);if(!/^SELECT\s/i.test(result.value?.sql_query||''))throw new Error('The rule filter is invalid for the selected registry. Check its fields and conditions.');}
  for(const k of ['quantity','max_quantity','decimal_places'])if(k in payload&&payload[k]<0)throw new Error(`${meta[k].string} cannot be negative.`);
  if(!record&&item.model==='g2p.enrollment.cycle'&&payload.program_id){const d=await call(item.model,'default_get',[['cycle_number']],{context:{default_program_id:payload.program_id}});if(!values.cycle_number||values.cycle_number===initial.cycle_number)payload.cycle_number=d.cycle_number;}
  if(!record&&item.model==='g2p.eligibility.rule.definition'&&payload.program_id){const d=await call(item.model,'default_get',[['rule_number']],{context:{default_program_id:payload.program_id}});if(!values.rule_number||values.rule_number===initial.rule_number)payload.rule_number=d.rule_number;}
  if(record){if(Object.keys(payload).length)await call(item.model,'write',[[record.id],payload]);}else await call(item.model,'create',[payload],{context});
  onSaved();
 }catch(e){setError(e.message);}finally{setBusy(false);}}
 return <div className="overlay"><section className="dialog" role="dialog" aria-modal="true" aria-label={`${record?'Edit':'New'} ${item.label}`}><div className="section-head"><h2>{record?'Edit':'New'} {item.label}</h2><button aria-label="Close form" onClick={onClose} disabled={busy}>✕</button></div>{error&&<p role="alert" className="error">{error}</p>}{!meta?<p>Loading form…</p>:<form onSubmit={submit}><div className="form-grid">{names.filter(k=>meta[k]).map(k=>{const f=meta[k];const disabled=busy||!!record&&['program_id','enrollment_cycle_id','disbursement_cycle_id','cycle_number','decimal_places','is_sponsor_bank'].includes(k);const val=values[k];const change=v=>setValues(s=>({...s,[k]:v}));let input;
 if(['many2one','many2many'].includes(f.type))input=<RelationInput field={{...f,required:f.required||k==='program_id'}} value={val} onChange={change} disabled={disabled} domain={k==='benefit_code_id'&&benefits!==null&&item.model!=='g2p.program.benefit.codes'?[['id','in',benefits]]:['enrollment_cycle_id','disbursement_cycle_id'].includes(k)&&values.program_id?[['program_id','=',scalar(values.program_id,{type:'many2one'})]]:[]}/>;
 else if(k==='multiplier')input=<select aria-label={f.string} value={val||''} onChange={e=>change(e.target.value)}><option value="">No multiplier</option>{multipliers.map(([v,l])=><option key={v} value={v}>{l}</option>)}</select>;
 else if(f.type==='boolean')input=<input type="checkbox" checked={!!val} disabled={disabled} onChange={e=>change(e.target.checked)}/>;
 else if(f.type==='selection')input=<select aria-label={f.string} required={f.required} disabled={disabled} value={val||''} onChange={e=>change(e.target.value)}><option value="">Select…</option>{f.selection.map(([v,l])=><option key={v} value={v}>{l}</option>)}</select>;
 else if(f.type==='text'||k==='pbms_domain')input=<textarea aria-label={f.string} required={f.required} disabled={disabled} rows={4} value={val||''} onChange={e=>change(e.target.value)}/>;
 else input=<input aria-label={f.string} required={f.required||k==='program_id'} disabled={disabled} type={['integer','float'].includes(f.type)?'number':f.type==='date'?'date':'text'} step={f.type==='float'?'any':undefined} value={val===false||val==null?'':val} onChange={e=>change(e.target.value)}/>;
 return <label key={k}>{f.string}{f.required?' *':''}{input}<small>{f.help||''}</small></label>;})}</div><footer><button type="button" onClick={onClose} disabled={busy}>Cancel</button><button className="primary" disabled={busy}>{busy?'Saving…':'Save record'}</button></footer></form>}</section></div>;
}

const links={
 'g2p.program.definition':[['programme-benefits','program_id'],['eligibility','program_id'],['entitlements','program_id'],['enrollment','program_id'],['disbursement','program_id'],['lists','program_id'],['agency-benefits','program_id'],['warehouse-benefits','program_id']],
 'g2p.enrollment.cycle':[['lists','enrollment_cycle_id']],
 'g2p.disbursement.cycle':[['priority','disbursement_cycle_id'],['lists','disbursement_cycle_id']],
 'g2p.agency':[['agency-benefits','agency_id']],
 'g2p.warehouse':[['warehouse-benefits','warehouse_id']],
};
export function Related({item,record,onNavigate,catalog}){return <div className="related-links">{(links[item.model]||[]).map(([key,field])=><button key={key} onClick={()=>onNavigate(key,{[field]:record.id})}>{catalog.find(c=>c.key===key)?.label} →</button>)}</div>;}
