"""Reconcile installed snapshots and ensure aggregate-only readers cannot mutate."""
import sys,json
from pathlib import Path
import psycopg2
sys.path.insert(0,'/opt/openg2p-lab/registration')
import registration_app as r
from service_reporting import SPECS,view_name
from flask import g
cfg=json.loads((r.ROOT/'analytics-connections.json').read_text())
verified=0
for service,spec in SPECS.items():
 with psycopg2.connect(**cfg['sources'][spec['database']]) as conn,conn.cursor() as cur:
  cur.execute('SHOW default_transaction_read_only');assert cur.fetchone()[0]=='on'
  cur.execute('SELECT rolsuper,rolcreatedb,rolcreaterole FROM pg_roles WHERE rolname=current_user');assert cur.fetchone()==(False,False,False)
  saved=r.one('SELECT * FROM analytics_source_cache WHERE source=?',(spec['source'],));assert saved and not saved['error']
  cached=json.loads(saved['payload'])
  for metric in spec['metrics']:
   name='nsipa_reporting.'+view_name(service,metric)
   cur.execute('SELECT label,value FROM '+name)
   live=[{'label':label,'value':float(value) if value is not None else None} for label,value in cur.fetchall()]
   assert sorted(live,key=lambda x:x['label'])==sorted(cached[metric],key=lambda x:x['label']),(service,metric)
   cur.execute("SELECT has_table_privilege(current_user,%s,'INSERT'),has_table_privilege(current_user,%s,'UPDATE'),has_table_privilege(current_user,%s,'DELETE')",(name,name,name));assert cur.fetchone()==(False,False,False)
   verified+=1
  # New source databases expose aggregate views, not personal data tables.
  raw={'socialregistrydb':'res_partner','portalpbmsdb':'res_partner','partner_management':'pm_partners','consent_manager':'consent_requests','iam':'staff_roles','odkdb':'submissions','superset':'ab_user','master_data':'g2p_attribute_values'}.get(spec['database'])
  if raw:
   cur.execute("SELECT has_table_privilege(current_user,%s,'SELECT')",(raw,));assert cur.fetchone()[0] is False,(service,'raw access')
with r.app.test_request_context('/registration/api/analytics'):
 g.user={'sub':'verification-only','name':'Verification','roles':['iqs-programme-supervisor']};g.session={'mode':'staff','csrf':'verification-only'};g.sid='verification-only';g.staff=False
 data=r.app.view_functions['analytics.api']()
 assert len(data['sources'])==15
 assert all(not s['stale'] and not s['error'] for s in data['sources'])
 catalogue=json.loads(Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/sitewide-ui/modules.json').read_text())
 assert {m['id'] for m in catalogue} <= set(data['allowed_services'])
 assert all(data['demo'][s]['record_count']==36 for s in ['odk','consent-manager'])
 assert len({x['record_id'] for d in data['demo'].values() for x in d['records']})==72
 print('PASS: 17 authorized service dashboards; 15 current sources;',verified,'new metrics reconciled; 72 distinct demo records; aggregate readers verified.')
with psycopg2.connect(**cfg['superset']) as conn,conn.cursor() as cur:
 cur.execute("SELECT COUNT(*) FROM aggregate_metrics WHERE source IN ('Geographic record data','Staff access administration')")
 assert cur.fetchone()[0]==0
print('PASS: supervisor-only sources excluded from the broader Superset dataset.')
