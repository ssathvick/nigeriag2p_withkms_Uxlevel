let context={};
export function setContext(value){context=value||{};}
export async function rpc(path,params={}){
 const response=await fetch(path,{method:'POST',credentials:'same-origin',headers:{'Content-Type':'application/json'},body:JSON.stringify({jsonrpc:'2.0',method:'call',params,id:Date.now()})});
 if(!response.ok)throw new Error(`The service returned ${response.status}. Please retry.`);
 const data=await response.json();
 if(data.error){
  const expired=data.error.code===100 || /SessionExpired/.test(data.error.data?.name||'');
  if(expired)window.dispatchEvent(new Event('pbms-session-expired'));
  throw new Error(expired?'Your session has expired. Please sign in again.':data.error.data?.message||data.error.message||'The request failed.');
 }
 return data.result;
}
export function call(model,method,args=[],kwargs={}){return rpc(`/web/dataset/call_kw/${model}/${method}`,{model,method,args,kwargs:{...kwargs,context:{...context,...kwargs.context}}});}
export function nativeUrl(item,id){return `/web?native=1#action=${item.action}&model=${item.model}${id?`&id=${id}&view_type=form`:'&view_type=list'}`;}
