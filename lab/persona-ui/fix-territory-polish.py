from pathlib import Path
p=Path('persona-ui/src/territories.jsx');s=p.read_text();s=s.replace('<small>{m.unit} <span aria-hidden="true">','<small>{name===\'poverty\'?\'share of residents\':m.unit} <span aria-hidden="true">');s=s.replace("function choose(id){setSelected(id);profile.current?.focus({preventScroll:true})}","function choose(id,reveal=false){setSelected(id);const next=all.find(a=>a.id===id);if(filter&&next&&(next.state_id||next.id)!==filter)setFilter('');profile.current?.focus({preventScroll:true});if(reveal)profile.current?.scrollIntoView({behavior:'smooth',block:'start'})}")
s=s.replace('onClick={()=>choose(a.id)}','onClick={()=>choose(a.id,true)}');s=s.replace("<dd>{nf.format(m.value)} {m.unit||''}</dd>","<dd>{m.unit==='index'?m.value.toFixed(3):m.unit==='%'?m.value.toFixed(1):nf.format(m.value)} {m.unit||''}</dd>")
s=s.replace("p.metric.value)} ↗", "p.metric.value)} ↗")
p.write_text(s)
p=Path('persona-ui/src/territories.css');p.write_text(p.read_text()+"\n.ti-profile{scroll-margin-top:25px}.ti-provenance,.ti-provenance>button,.ti-class{font-size:10px}.ti-metric-main:hover strong{color:#2d8a60}.ti-coverage button:hover strong{color:#2d8a60}\n")
