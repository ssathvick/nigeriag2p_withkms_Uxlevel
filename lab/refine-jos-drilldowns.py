from pathlib import Path
p=Path('persona-ui/src/jos-cct.jsx');s=p.read_text().replace("(!filter||r[filter.key]===filter.value)","(!filter||(filter.key==='grievance'&&filter.value==='Needs review'?['Open','Payment query'].includes(r.grievance):filter.key==='payment'&&filter.value==='Received'?['Confirmed','Reconciled'].includes(r.payment):r[filter.key]===filter.value))")
s=s.replace("onClick={()=>go('Casework')}/>","onClick={()=>go('Casework',{key:'grievance',value:'Needs review'})}/>")
s=s.replace("onClick={()=>go('Payments')}/>","onClick={()=>drill('payment','Received')}/>")
s=s.replace("sub=\"Cycle 01 · simulated receipt value\" onClick={()=>setFilter(null)}","sub=\"Cycle 01 · simulated receipt value\" onClick={()=>drill('payment','Received')}")
s=s.replace("['Not scheduled','Ready','Approved','Submitted','Confirmed','Reconciled','Failed']:tab==='Casework'?['Open'", "['Received','Not scheduled','Ready','Approved','Submitted','Confirmed','Reconciled','Failed']:tab==='Casework'?['Needs review','Open'")
p.write_text(s)
