import React,{useState,useEffect} from 'react';
export default function RepresentativeActivity({representative:r}){
 const [category,setCategory]=useState(''),[year,setYear]=useState('');
 useEffect(()=>{setCategory('');setYear('')},[r.id]);
 const events=r.evidence||[],years=[...new Set(events.map(e=>String(e.reference_year)))].sort().reverse();
 const cohort=events.filter(e=>!year||String(e.reference_year)===year);
 const categories=[...new Set(events.map(e=>e.category))];
 const shown=cohort.filter(e=>!category||e.category===category);
 return <section className="ti-panel"><div className="ti-section-title"><h3>Documented activity</h3><label>Activity evidence year<select value={year} onChange={e=>setYear(e.target.value)}><option value="">All documented years</option>{years.map(y=><option key={y}>{y}</option>)}</select></label></div><p>Published reports, individually sourced. These are partial activity records, not complete tenure totals, outcome scores or attendance rates.</p>
 <div className="ti-rep-metrics">{['',...categories].map(c=><button key={c} className={category===c?'selected':''} onClick={()=>setCategory(c)}><span>{c||'All documented activity'}</span><strong>{cohort.length?cohort.filter(e=>!c||e.category===c).length:'Unavailable'}</strong><small>View source records ↓</small></button>)}</div>
 <div aria-live="polite"><p>{shown.length} matching records · {year||'all documented years'}</p>{shown.map(e=><article key={e.id}><h4><a href={e.source_url} target="_blank" rel="noreferrer">{e.title} ↗</a></h4><p>{e.summary}</p><small>{e.date} · reference year {e.reference_year} · {e.source_name} · {e.level} · Published data</small><p>{e.status}. {e.qualification}</p><details><summary>Date and attribution</summary><p>{e.date_basis||'Report publication date; event timing follows the source.'}</p><p>{e.attribution}</p></details></article>)}</div>
 {!shown.length&&<p>No sufficiently verified named-person activity record is loaded for this selection. Missing evidence is not zero performance.</p>}</section>
}
