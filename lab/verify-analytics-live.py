"""Read only source reconciliation and rendering from the installed application."""
import sys,json
from pathlib import Path
sys.path.insert(0,'/opt/openg2p-lab/registration')
import registration_app as r
from flask import g
import requests,psycopg2
cfg=json.loads((r.ROOT/'analytics-connections.json').read_text())
with r.app.test_request_context('/registration/analytics'):
 g.user={'sub':'qa-render','name':'Analytics preview','roles':['iqs-programme-supervisor']}
 g.staff=False;g.session={'mode':'staff','csrf':'preview-only'};g.sid='preview-only'
 report=r.app.view_functions['analytics.api']()
 assert all(not s['error'] and not s['stale'] for s in report['sources'])
 assert report['operations']['profiles']==r.one('SELECT COUNT(*) AS n FROM profiles')['n']
 assert report['knowledge']['live']==r.one("SELECT COUNT(*) AS n FROM km_articles WHERE published IS NOT NULL AND status!='archived'")['n']
 html=r.app.view_functions['analytics.dashboard']()
 css=(r.ROOT/'static/style.css').read_text()
 html=html.replace('<link rel="stylesheet" href="/registration/static/style.css">','<style>'+css+'</style>')
 output=Path('/mnt/h/Nigeria_Mosip/codex/outputs/analytics-client-guide/installed-analytics-preview.html')
 output.write_text(html)
 print('Native counts reconciled. Backend sources healthy:',len(report['sources']))
for name,connection in cfg['sources'].items():
 with psycopg2.connect(**connection) as conn,conn.cursor() as cur:
  cur.execute('SHOW default_transaction_read_only');assert cur.fetchone()[0]=='on'
  cur.execute("SELECT rolsuper,rolcreatedb,rolcreaterole FROM pg_roles WHERE rolname=current_user");assert cur.fetchone()==(False,False,False)
  if name=='register':
   cur.execute("SELECT has_table_privilege(current_user,'g2p_register_individuals','INSERT')");assert cur.fetchone()[0] is False
with psycopg2.connect(**cfg['superset']) as conn,conn.cursor() as cur:
 cur.execute('SELECT COUNT(*) FROM aggregate_metrics');assert cur.fetchone()[0]>0
 cur.execute("SELECT has_table_privilege(current_user,'aggregate_metrics','INSERT')");assert cur.fetchone()[0] is False
print('Dedicated source and Superset identities verified read only.')
response=requests.get('http://127.0.0.1:18081/registration/api/analytics',timeout=10)
assert response.status_code==401
assert requests.get('http://127.0.0.1:18081/registration/static/analytics.js',timeout=10).status_code==200
print('Live anonymous analytics blocked. Tracking script available.')
