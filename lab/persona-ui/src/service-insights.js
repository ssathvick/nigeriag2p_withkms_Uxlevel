import {modules} from './catalogue';
import './service-insights.css';
// Read only the records already rendered by the user's authorized application.
// No requests, credentials, record persistence, or writes to native workflows.
const module=modules.find(m=>m.host===location.hostname&&m.host!=='nigeriag2p.com');
if(module&&window.self===window.top){
 let panel,opener,observer,timer,signature='',selection='',query='',snapshot=null,opened=false,shownOnce=false;
 const node=(tag,cls,text)=>{const el=document.createElement(tag);if(cls)el.className=cls;if(text!==undefined)el.textContent=text;return el};
 const visible=el=>!!(el.getClientRects().length)&&getComputedStyle(el).visibility!=='hidden'&&!el.closest('[aria-hidden="true"]');
 const text=el=>(el?.innerText||'').replace(/ⓘ/g,'').trim().replace(/\s+/g,' ');
 function extract(){
  // Login and password screens must retain their native presentation.
  if([...document.querySelectorAll('input[type=password]')].some(visible)||/\/(login|signin|auth)(\/|$)/i.test(location.pathname))return null;
  const tables=[...document.querySelectorAll('table,[role="grid"],[role="table"]')].filter(t=>!t.closest('#nsipa-insights')&&visible(t));
  const candidates=tables.map(t=>{const headers=[...t.querySelectorAll('thead th,[role="columnheader"]')].map(text);const records=[...t.querySelectorAll('tbody tr,[role="row"]')].filter(r=>!r.querySelector('th,[role="columnheader"]')&&!r.matches('.o_group_header,.o_group_has_content')&&visible(r)).map(r=>[...r.querySelectorAll('td,[role="gridcell"],[role="cell"]')].map(text)).filter(c=>c.length>1&&c.some(Boolean));return {headers,records}}).filter(t=>t.records.length);
  if(module.id==='register'){
   const links=[...document.querySelectorAll('a[href]')].filter(a=>visible(a)&&/\/register\/(household|individual)\/[^/]+$/.test(new URL(a.href).pathname)&&a.querySelector('h3'));
   if(links.length){
    const objects=links.map(a=>{const values={'Record':text(a.querySelector('h3'))};a.querySelectorAll('p').forEach(p=>{const spans=p.querySelectorAll('span');if(spans.length>=2){const key=text(spans[0]).replace(/:$/,'').trim();if(key)values[key]=text(spans[1])}});return values});
    const headers=[...new Set(objects.flatMap(o=>Object.keys(o)))];
    const statusIndex=headers.findIndex(h=>/^(gender|sex|household size total|tenure status|dwelling type)$/i.test(h)&&objects.some(o=>o[h]));
    return {headers,records:objects.map(o=>headers.map(h=>o[h]||'')),statusIndex,labelIndex:0,cardList:true};
   }
  }
  if(!candidates.length)return null;
  const best=candidates.sort((a,b)=>b.records.length-a.records.length)[0];
  const statusIndex=best.headers.findIndex(h=>/\b(status|state|stage|approval)\b/i.test(h)&&!/state\s*(\/|or|name|code|fct)/i.test(h));
  // A bare State column can mean geography, so never infer workflow status from it.
  const safeStatus=statusIndex>=0&&!/^state$/i.test(best.headers[statusIndex])?statusIndex:-1;
  const dimension=safeStatus>=0?safeStatus:best.headers.findIndex(h=>/\b(type|category|gender|sex|unit)\b/i.test(h));
  const labelIndex=best.headers.findIndex(h=>/\b(name|title|reference|mnemonic)\b/i.test(h));
  return {...best,statusIndex:dimension,cardList:safeStatus<0,labelIndex:labelIndex>=0?labelIndex:best.headers.findIndex(h=>!!h)};
 }
 function close(){panel.hidden=true;opened=false;opener.setAttribute('aria-expanded','false');opener.focus()}
 function toggle(){opened=!opened;panel.hidden=!opened;opener.setAttribute('aria-expanded',String(opened));if(opened){update();panel.querySelector('button')?.focus()}}
 function start(){
  opener=node('button','nsipa-insight-open','◈ Visual overview');opener.id='nsipa-insight-open';opener.type='button';opener.hidden=true;opener.setAttribute('aria-controls','nsipa-insights');opener.setAttribute('aria-expanded','false');opener.addEventListener('click',toggle);
  panel=node('section','');panel.id='nsipa-insights';panel.hidden=true;panel.setAttribute('aria-label',module.title+' visual overview');panel.addEventListener('keydown',e=>{if(e.key==='Escape')close()});document.body.append(opener,panel);
  observer=new MutationObserver(changes=>{if(changes.every(c=>c.target===panel||panel.contains(c.target)||c.target===opener))return;if(!timer)timer=setTimeout(()=>{timer=null;update()},350)});
  observer.observe(document.documentElement,{childList:true,subtree:true,characterData:true,attributes:true,attributeFilter:['class','hidden','aria-hidden']});window.addEventListener('popstate',update);window.addEventListener('hashchange',update);document.addEventListener('visibilitychange',()=>{if(!document.hidden)update()});update();
 }
 function update(){if(!panel.isConnected||!opener.isConnected)document.body.append(opener,panel);const next=extract();const nextSignature=JSON.stringify(next);if(nextSignature===signature)return;signature=nextSignature;snapshot=next;selection='';query='';if(!next){opener.hidden=true;panel.hidden=true;opened=false;opener.setAttribute('aria-expanded','false');return}opener.hidden=false;render();if(!shownOnce){shownOnce=true;opened=true;panel.hidden=false;opener.setAttribute('aria-expanded','true')}}
 function render(){if(!snapshot)return;const focused=document.activeElement?.id;const position=document.activeElement?.selectionStart;panel.replaceChildren();
  const header=node('div','nsi-head');const heading=node('div');heading.append(node('small','','CURRENT VIEW INSIGHTS'),node('h2','',module.title));const closeBtn=node('button','nsi-close','Close ×');closeBtn.type='button';closeBtn.addEventListener('click',close);header.append(heading,closeBtn);panel.append(header,node('p','nsi-scope','Based only on the loaded rows in your current record list. Search, pagination and application filters can change this view.'));
  const records=snapshot.records;const grouped=Object.create(null);if(snapshot.statusIndex>=0)records.forEach(row=>{const status=row[snapshot.statusIndex]||'Not recorded';grouped[status]=(grouped[status]||0)+1});
  const cards=node('div','nsi-stats');[['Loaded records',records.length],['Displayed fields',snapshot.headers.filter(Boolean).length],[snapshot.cardList?'Record categories':'Workflow categories',snapshot.statusIndex>=0?Object.keys(grouped).length:'—']].forEach(([label,value])=>{const card=node('div');card.append(node('small','',label),node('strong','',String(value)));cards.append(card)});panel.append(cards);
  if(snapshot.statusIndex>=0){panel.append(node('h3','',snapshot.headers[snapshot.statusIndex]+' breakdown'));const chart=node('div','nsi-chart');Object.entries(grouped).sort((a,b)=>b[1]-a[1]).forEach(([status,count])=>{const button=node('button','nsi-status');button.type='button';button.setAttribute('aria-pressed',String(selection===status));const line=node('span','nsi-line');line.append(node('span','',status),node('b','',`${count} · ${Math.round(count/records.length*100)}%`));const track=node('span','nsi-track');const fill=node('span');fill.style.width=count/records.length*100+'%';track.append(fill);button.append(line,track);button.addEventListener('click',()=>{selection=selection===status?'':status;render()});chart.append(button)});panel.append(chart)}else panel.append(node('p','nsi-scope','This list does not expose a workflow status column. Open a status-based record list to see its distribution.'));
  const labelEl=node('label','nsi-search','Find a loaded record');const input=node('input');input.id='nsi-record-search';input.type='search';input.placeholder='Filter this overview…';input.value=query;input.addEventListener('input',e=>{query=e.target.value;render()});labelEl.append(input);panel.append(labelEl);
  const filtered=records.filter(r=>(!selection||r[snapshot.statusIndex]===selection)&&r.join(' ').toLowerCase().includes(query.toLowerCase()));const summary=node('p','nsi-scope',`${filtered.length} of ${records.length} loaded rows${selection?' · '+selection:''}. The underlying record list is unchanged.`);summary.setAttribute('role','status');panel.append(summary);
  const list=node('ul','nsi-records');filtered.slice(0,50).forEach((r,i)=>{const item=node('li');item.append(node('span','',r[snapshot.labelIndex]||`Row ${i+1}`));if(snapshot.statusIndex>=0)item.append(node('small','',r[snapshot.statusIndex]||'Not recorded'));list.append(item)});if(!filtered.length)list.append(node('li','','No loaded rows match. Clear the search or selected status.'));panel.append(list);if(filtered.length>50)panel.append(node('small','nsi-scope','Showing the first 50 matching rows. Narrow this overview to find a record.'));
  const footer=node('div','nsi-foot');const a=node('a','','Open service dashboard ↗');a.href='https://nigeriag2p.com/registration/analytics?service='+encodeURIComponent(module.id);footer.append(a,node('small','','Updates as the application changes.'));panel.append(footer);
  if(focused==='nsi-record-search'){input.focus();input.setSelectionRange(position,position)}
 }
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',start,{once:true});else start();
}
