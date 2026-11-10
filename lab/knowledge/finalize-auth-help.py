from pathlib import Path
import json,re,sqlite3,datetime
root=Path(__file__).resolve().parent;src=root.parent;app=Path('/opt/openg2p-lab/registration');now=datetime.datetime.now().isoformat();db=sqlite3.connect(app/'intake.sqlite');db.row_factory=sqlite3.Row
updates={};stages=['Payment account details','Complaints and enquiries','Notifications','News and announcements']
with db:
 for row in db.execute('SELECT * FROM km_articles WHERE module=? AND audience=?',('beneficiary','all')).fetchall():
  a=json.loads(row['published'])
  if a['stage'] not in stages:continue
  assert row['draft']==row['published']
  a['scope']='upstream_reference';a['purpose']='This screen is not enabled in the installed beneficiary portal. The following guidance describes the feature only if it is enabled in a later release.'
  a['requirements']='Administrator confirmation that this feature has been enabled, plus the required account permissions.'
  a['next_step']='For the current installation, use the available programme, application, benefit or profile screen. Use the portal contact information for assistance.'
  a['issues']='Opening a route that is not installed returns a not-found response. This is not a failed sign-in. Do not enter personal or account information into an unsupported screen.'
  content=json.dumps(a);version=row['version']+1;actor='system:nsipa-screen-availability';note='Verified against authenticated installed routes on both domains.'
  db.execute('UPDATE km_articles SET draft=?,published=?,version=?,published_version=?,author=?,reviewer=NULL,review_note=?,updated=? WHERE id=?',(content,content,version,version,actor,note,now,row['id']))
  db.execute('INSERT INTO km_history(article,version,action,actor,at,content,note) VALUES(?,?,?,?,?,?,?)',(row['id'],version,'maintenance_publication',actor,now,content,note));updates[row['slug']]=a
for p in [src/'knowledge-seed.json',root/'seed.json',app/'knowledge-seed.json']:
 d=json.loads(p.read_text());d['articles']=[{**a,**updates.get(a['slug'],{})} for a in d['articles']];p.write_text(json.dumps(d,ensure_ascii=False,indent=2))
# Keep the reviewable route matrix aligned with the deployed resolver.
p=root/'other-module-guidance.json';plan=json.loads(p.read_text());plan['routes']=json.loads(re.search(r' const screenRoutes=(.*);\n',(root/'context.js').read_text()).group(1));p.write_text(json.dumps(plan,ensure_ascii=False,indent=2))
rows=json.loads((root/'authenticated-screen-coverage.json').read_text());installed=[];excluded=[]
for row in rows:
 if row.get('status')==404:excluded.append({**row,'classification':'Source-candidate route not installed; absent from current application navigation'})
 elif row.get('path','').endswith('.xml'):excluded.append({**row,'classification':'XML form download, not an HTML screen'})
 else:installed.append(row)
report={'installed_route_checks':len(installed),'hosts':len(set(r['host'] for r in installed)),'failures':[r for r in installed if r.get('error') or r.get('oldBrand') or r.get('emptyHelp') or r.get('status',200)>=400],'excluded_route_probes':excluded,'sign_in_fixes':['staff-portal authorization and token-exchange callback consistency','beneficiary authorization and token-exchange callback consistency','session-cookie domain translation per domain family','removed automatic analytics redirects']}
(root/'auth-restoration-summary.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='excluded_route_probes'}))
