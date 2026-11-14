from pathlib import Path
root=Path(__file__).parent
def patch(path,old,new):
 p=root/path;s=p.read_text(encoding='utf-8')
 if new in s:return
 if old not in s:raise RuntimeError('Missing source anchor '+str(path))
 p.write_text(s.replace(old,new),encoding='utf-8')
patch(Path('registration_app.py'),"'mbr':request.args.get('mbr')=='1',","'mbr_return':g.session.get('mbr_return'),'mbr':request.args.get('mbr')=='1',")
patch(Path('registration_app.py'),"if flow.get('mbr'):return redirect(PREFIX+'/mbr')", "if flow.get('mbr'):return redirect(flow.get('mbr_return') if str(flow.get('mbr_return') or '').startswith(PREFIX+'/mbr?') else PREFIX+'/mbr')")
patch(Path('persona-ui/src/mbr.jsx'),"if(submit)nav(editing.master?'changes':'submissions','Pending',result.id)","if(submit)nav(editing.master||current?.kind==='change'?'changes':'submissions','Pending',result.id)")
patch(Path('persona-ui/src/mbr.jsx'),'https://g2p-register.wverve.in/en?_nsipa_records=1','https://g2p-register.wverve.in/en?native_view=1&_nsipa_records=1')
patch(Path('persona-ui/src/mbr.jsx'),"s.payload?.members?.length||0","s.payload?.members?.length||s.payload?.declared_household_size||0")
patch(Path('persona-ui/src/dashboard-navigation.js'),"export function recordsUrl(service,metric='',category='',personal=false){", "export function recordsUrl(service,metric='',category='',personal=false){\n if(service==='register')return markRecords('https://g2p.wverve.in/registration/mbr?view='+(metric==='change_request_status'?'changes':category.toLowerCase().includes('individual')?'individuals':'registers'));")
