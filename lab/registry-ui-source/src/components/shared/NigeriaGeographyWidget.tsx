'use client';
import {useEffect,useState} from 'react';
import {useBaseWidget,widgetRegistry,type BaseWidgetConfig} from '@openg2p/registry-widgets';
type Place={id:string;name:string;parent?:string};type Catalogue={states:Place[];lgas:Place[];wards:Place[]};
let request:Promise<Catalogue>|undefined;
function NigeriaGeographyWidget({config}:{config:BaseWidgetConfig}){
 const {value,onChange,isEnabled,getFieldValue}=useBaseWidget({config});const [data,setData]=useState<Catalogue|null>(null),[failed,setFailed]=useState(false);
 useEffect(()=>{request??=fetch('/data/nigeria-locations.json').then(r=>{if(!r.ok)throw Error('Location catalogue unavailable');return r.json()});request.then(setData).catch(()=>{request=undefined;setFailed(true)});},[]);
 const dataPath=config['widget-data-path'];const rawHierarchy=typeof dataPath==='object'?getFieldValue(dataPath.hierarchy):null;const hierarchy=rawHierarchy?.hierarchy||[];const selected=(level:string)=>hierarchy.find((x:any)=>x.level===level)?.level_value_id||'';const state=selected('state'),lga=selected('lga'),ward=selected('ward');
 const choose=(level:string,id:string)=>{
  if(!data)return;const items:any[]=[{level:'country',level_value_id:'NG',level_value_mnemonic:'Nigeria'}];
  const ids={state:level==='state'?id:state,lga:level==='state'?'':level==='lga'?id:lga,ward:level==='ward'?id:''};
  for(const[k,collection]of [['state','states'],['lga','lgas'],['ward','wards']]as const){const p=data[collection].find(p=>p.id===ids[k]);if(!p)break;items.push({level:k,level_value_id:p.id,level_value_mnemonic:p.name});}
  const last=items[items.length-1];onChange({value:last.level_value_id,hierarchy:{hierarchy:items,lowest_level_value_id:last.level_value_id}});
 };
 if(config['widget-readonly'])return <div className="text-sm"><strong>Administrative location: </strong>{hierarchy.map((x:any)=>x.level_value_mnemonic).join(' / ')||'Not recorded'}</div>;
 return <fieldset className="rounded-lg border border-primary-second p-4" aria-label="Nigeria administrative location"><legend className="px-2 font-semibold">Nigeria administrative location</legend><p className="mb-3 text-sm">Country: Nigeria. Select State / FCT, Local Government Area and ward from the reference catalogue.</p>{failed?<p role="alert">Location choices could not load. Save a draft and try again when connected.</p>:<div className="grid gap-4 sm:grid-cols-3">{([['state','State / FCT',data?.states||[],state],['lga','Local Government Area',(data?.lgas||[]).filter(p=>p.parent===state),lga],['ward','Ward',(data?.wards||[]).filter(p=>p.parent===lga),ward]]as const).map(([key,label,places,id])=><label key={key} className="flex flex-col gap-2 text-sm" htmlFor={config['widget-id']+'-'+key}><span>{label}</span><select aria-label={label} id={config['widget-id']+'-'+key} value={id} disabled={!isEnabled||!data||(key==='lga'&&!state)||(key==='ward'&&!lga)} onChange={e=>choose(key,e.target.value)} className="rounded-lg border bg-white px-3 py-2"><option value="">Select {label}</option>{places.map(p=><option key={p.id} value={p.id}>{p.name}</option>)}</select></label>)}</div>}<p className="mt-3 text-xs">Changing a parent area clears the dependent selections. This is the same reference catalogue used by mobile registration.</p></fieldset>;
}
widgetRegistry.register({widget:'geo-hierarchy',component:NigeriaGeographyWidget});
export default NigeriaGeographyWidget;
