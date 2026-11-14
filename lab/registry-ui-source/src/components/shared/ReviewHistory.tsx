'use client';
export function ReviewHistory({events=[]}:{events?:Array<{event_type:string;actor?:string;occurred_at?:string;stage_order?:number;request_id?:string;reason?:string}>}){
 if(!events.length)return null;
 return <details className="rounded-lg border border-primary-first bg-white p-5"><summary className="cursor-pointer font-semibold">Approval history · {events.length} events</summary><ol className="mt-4 space-y-3">{events.map((e,i)=><li key={i} className="border-l-2 border-primary-first pl-4"><strong>{e.event_type.replaceAll('_',' ')}</strong>{e.stage_order?` · Stage ${e.stage_order}`:''}<p className="text-sm">{e.actor||'Workflow'} · {e.occurred_at?new Date(e.occurred_at).toLocaleString():''}</p>{e.reason&&<p className="whitespace-pre-wrap">{e.reason}</p>}</li>)}</ol></details>;
}
