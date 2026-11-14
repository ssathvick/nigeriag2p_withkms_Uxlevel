"""Keep the existing portal entry points and callback aware of the MBR workspace."""
from pathlib import Path
root=Path(__file__).parent
def patch(path, old, new):
    p=root/path;s=p.read_text(encoding='utf-8')
    if new not in s:
        if old not in s:raise RuntimeError('Patch anchor missing: '+str(p))
        p.write_text(s.replace(old,new),encoding='utf-8')
patch(Path('registration_app.py'),"'workspace':request.args.get('workspace')=='1',", "'mbr':request.args.get('mbr')=='1','workspace':request.args.get('workspace')=='1',")
patch(Path('registration_app.py')," if flow.get('beneficiary_profile'):"," if flow.get('mbr'):return redirect(PREFIX+'/mbr')\n if flow.get('beneficiary_profile'):")
patch(Path('registration_app.py'),"def default_login_destination(mode,roles):", "def default_login_destination(mode,roles):\n if mode=='staff' and any(role.startswith('mbr-') for role in roles):return PREFIX+'/mbr'")
patch(Path('registration_app.py'),"request.path.startswith(PREFIX+'/api/')", "(request.path.startswith(PREFIX+'/api/') or request.path.startswith(PREFIX+'/mbr/api/'))")
patch(Path('persona-ui/src/site.jsx'),'<nav aria-label="Platform navigation">','<nav aria-label="Platform navigation"><a href="/registration/mbr">MBR workspace</a>')
patch(Path('registration-ui/base.html'),'<nav><a href="{{prefix}}/mobile">','<nav><a href="{{prefix}}/mbr">MBR workspace</a><a href="{{prefix}}/mobile">')
patch(Path('persona-ui/src/mbr.jsx'),"const next=[...queue,{client_id:crypto.randomUUID(),data:clone(p),captured_at:new Date().toISOString()}];", "const item={client_id:editing.queueId||crypto.randomUUID(),data:clone(p),captured_at:new Date().toISOString()};const next=editing.queueId?queue.map(q=>q.client_id===editing.queueId?item:q):[...queue,item];")
patch(Path('persona-ui/src/mbr.jsx'),"setEditing({initial:q.data,offline:true});storeQueue(queue.filter(x=>x.client_id!==q.client_id))", "setEditing({initial:q.data,offline:true,queueId:q.client_id})")
patch(Path('persona-ui/src/mbr.jsx'),"{reveal?'◉ Hide':'◉ Reveal'}", "{reveal?'👁 Hide':'👁 Reveal'}")
patch(Path('persona-ui/src/mbr.jsx'),'<a href="/registration/workspace">Staff workspace ↗</a>', '<a href="/registration/workspace">Staff workspace ↗</a><form method="post" action="/registration/logout"><input type="hidden" name="csrf" value={csrf}/><button type="submit">Sign out</button></form>')
patch(Path('persona-ui/src/mbr.jsx'),"JSON.stringify(x,null,2)","JSON.stringify(x,(key,value)=>key==='id'?undefined:value,2)")
patch(Path('persona-ui/src/mbr.jsx'),"{isMaster?data.household_id:data.source}","{data.household_id||data.source}")
patch(Path('persona-ui/src/mbr.jsx'),"value.map(m=>`${name(m)} · ${m.relationship} · ${m.sex} · ${m.age} years`).join('\\n')", "value.map(m=>`${name(m)}\\n${Object.entries(m).filter(([k])=>k!=='id').map(([k,v])=>k.replaceAll('_',' ')+': '+stringify(v)).join('\\n')}`).join('\\n\\n')")
patch(Path('persona-ui/src/mbr.jsx'),'<span>{icon}</span>{label}','<span aria-hidden="true">{icon}</span>{label}')
patch(Path('persona-ui/src/mbr.jsx'),"Object.entries(data.pyramid).map(([band,v])=>", "['0–4','5–17','18–34','35–59','60+'].map(band=>{const v=data.pyramid[band];return [band,v]}).map(([band,v])=>")
