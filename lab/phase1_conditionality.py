"""Fictional CCT conditionality and approval demonstration; never dispatches funds."""
import datetime as dt,re,uuid
from flask import Blueprint,abort,g,request,redirect

def install(r,db,locations):
 bp=Blueprint('phase1_conditionality',__name__)
 author={'iqs-registration-officer','iqs-programme-supervisor','iqs-intake-reviewer'}
 reviewer={'iqs-verification-officer','iqs-intake-reviewer'}
 supervisor={'iqs-programme-supervisor','iqs-intake-reviewer'}
 with db() as c:c.execute('CREATE TABLE IF NOT EXISTS conditionality(id TEXT PRIMARY KEY,household TEXT NOT NULL,period TEXT NOT NULL,attendance INTEGER NOT NULL,maker TEXT NOT NULL,reviewer TEXT,status TEXT NOT NULL,version INTEGER NOT NULL,updated TEXT NOT NULL,UNIQUE(household,period))')
 def roles():
  r.require_user()
  if g.session.get('mode')!='staff':abort(403)
  current=set(g.user.get('roles',[]))
  if not current.intersection(author|reviewer|supervisor):abort(403)
  return current
 def rows():
  with db() as c:return [dict(x) for x in c.execute('SELECT * FROM conditionality ORDER BY updated DESC LIMIT 200')]
 @bp.get(r.PREFIX+'/phase1/conditionality')
 def page():
  current=roles();return r.page('phase1-conditionality.html',conditions=rows(),locations=locations,can_author=bool(current&author),can_review=bool(current&reviewer),can_release=bool(current&supervisor),subject=g.user['sub'])
 @bp.get(r.PREFIX+'/api/phase1/conditionality')
 def api():
  roles();return {'synthetic':True,'rule':'Fictional DEMO-CCT attendance at least 80 percent; monthly period; no actual payment','cases':[{k:v for k,v in x.items() if k not in ('maker','reviewer')} for x in rows()]}
 @bp.post(r.PREFIX+'/phase1/conditionality')
 def create():
  if not roles()&author:abort(403)
  ref=request.form.get('household');period=request.form.get('period','');attendance=request.form.get('attendance','')
  if ref not in {x[0] for x in locations} or not re.fullmatch(r'20\d\d-(0[1-9]|1[0-2])',period) or not re.fullmatch(r'\d{1,3}',attendance):abort(400,'Use a fictional household, YYYY-MM period and attendance from 0 to 100.')
  value=int(attendance)
  if not 0<=value<=100:abort(400)
  with db() as c:
   c.execute('BEGIN IMMEDIATE');old=c.execute('SELECT * FROM conditionality WHERE household=? AND period=?',(ref,period)).fetchone()
   if old:
    if old['maker']!=g.user['sub'] or old['attendance']!=value:abort(409,'This period already has evidence. Do not overwrite a decision.')
   else:
    cid=str(uuid.uuid4());c.execute("INSERT INTO conditionality VALUES(?,?,?,?,?,NULL,'pending_review',1,?)",(cid,ref,period,value,g.user['sub'],r.stamp()))
    c.execute('INSERT INTO events(reference,actor,action,at) VALUES(?,?,?,?)',(cid,g.user['sub'],'fictional_conditionality_submitted',r.stamp()))
  return redirect(r.PREFIX+'/phase1/conditionality')
 @bp.post(r.PREFIX+'/phase1/conditionality/<cid>/<action>')
 def decide(cid,action):
  current=roles()
  if action not in ('verify','release','hold'):abort(404)
  if not current&(reviewer if action=='verify' else supervisor):abort(403)
  with db() as c:
   c.execute('BEGIN IMMEDIATE');row=c.execute('SELECT * FROM conditionality WHERE id=?',(cid,)).fetchone()
   if not row:abort(404)
   if request.form.get('version')!=str(row['version']):abort(409,'Refresh this record before acting.')
   if action=='verify':
    if row['maker']==g.user['sub']:abort(403,'A different officer must verify submitted evidence.')
    if row['status']!='pending_review':abort(409)
    status='verified_pass' if row['attendance']>=80 else 'verified_fail'
    c.execute('UPDATE conditionality SET reviewer=? WHERE id=?',(g.user['sub'],cid))
   else:
    if row['status'] not in ('verified_pass','verified_fail'):abort(409)
    if action=='release' and row['status']!='verified_pass':abort(409,'Attendance below the fictional threshold must remain on hold.')
    if g.user['sub'] in (row['maker'],row['reviewer']):abort(403,'A third officer must make the release or hold decision.')
    status='released' if action=='release' else 'held'
   c.execute('UPDATE conditionality SET status=?,version=version+1,updated=? WHERE id=?',(status,r.stamp(),cid))
   c.execute('INSERT INTO events(reference,actor,action,at) VALUES(?,?,?,?)',(cid,g.user['sub'],'fictional_conditionality_'+action,r.stamp()))
  return redirect(r.PREFIX+'/phase1/conditionality')
 r.app.register_blueprint(bp)
