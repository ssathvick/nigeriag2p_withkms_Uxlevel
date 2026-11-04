from pathlib import Path
p=Path('jos_connected.py');s=p.read_text()
needle=" @bp.get(r.PREFIX+'/api/jos-cct')"
route=""" @bp.get(r.PREFIX+'/jos-cct/minister')
 def minister():
  if not g.user:return redirect(r.PREFIX+'/login?mode=staff&jos=1&minister=1')
  r.require_staff();key=request.args.get('sample','JOS-NATIVE-002')
  if key not in IDS:abort(404)
  try:step=int(request.args.get('step','1'))
  except ValueError:abort(400)
  if step not in range(1,9):abort(400)
  data=snapshot(r);publish(r,data);row=next(x for x in data['rows'] if x['id']==key)
  stages=[minister_stage(row,n) for n in range(1,9)]
  return r.page('jos-minister.html',data=data,row=row,stage=stages[step-1],stages=stages,panel=request.args.get('panel')=='1',message=request.args.get('message',''),error=request.args.get('error')=='1')
"""
s=s.replace(needle,route+needle)
s=s.replace("except GuardError as e:abort(409,str(e))\n  return redirect", """except GuardError as e:
   if request.form.get('minister')=='1' and key in IDS:
    return redirect(r.PREFIX+'/jos-cct/minister?sample='+key+'&step='+str(max(1,min(8,request.form.get('step',1,type=int) or 1)))+'&error=1&message='+requests.utils.quote(str(e)))
   abort(409,str(e))
  if request.form.get('minister')=='1':
   return redirect(r.PREFIX+'/jos-cct/minister?sample='+key+'&step='+str(max(1,min(8,request.form.get('step',1,type=int) or 1)))+'&message='+requests.utils.quote(message))
  return redirect""")
p.write_text(s)
p=Path('registration_app.py');s=p.read_text().replace("g.session['login']['jos']=request.args.get('jos')=='1'","g.session['login']['jos']=request.args.get('jos')=='1'\n g.session['login']['jos_minister']=request.args.get('minister')=='1'").replace("if flow.get('jos'):return redirect(PREFIX+'/jos-cct')","if flow.get('jos'):return redirect(PREFIX+'/jos-cct'+('/minister' if flow.get('jos_minister') else ''))");p.write_text(s)
p=Path('install-jos-connected.py');s=p.read_text().replace("(src/'registration-ui/jos-connected.html',root/'templates/jos-connected.html')","(src/'registration-ui/jos-connected.html',root/'templates/jos-connected.html'),(src/'registration-ui/jos-minister.html',root/'templates/jos-minister.html')");p.write_text(s)
