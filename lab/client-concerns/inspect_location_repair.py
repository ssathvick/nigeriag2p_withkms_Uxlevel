import sys,json,subprocess
from pathlib import Path
sys.path.insert(0,'/opt/openg2p-lab/registration')
import registration_app as r
RID='18023d14-0bc7-51a7-b51b-9f9b77ef8a05'
with r.pg('register') as c:
 with c.cursor() as q:
  q.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND (table_name LIKE '%household%' OR table_name LIKE '%history%')")
  print('TABLES',q.fetchall())
  q.execute("SELECT section_ui_schema FROM g2p_register_sections WHERE section_id='hh_location_details'")
  print('SCHEMA',json.dumps(q.fetchall()))
  q.execute('SELECT row_to_json(h) FROM g2p_register_households h WHERE internal_record_id=%s',(RID,))
  print('HOUSEHOLD',json.dumps(q.fetchall(),default=str))
with r.pg('master_data') as c:
 with c.cursor() as q:
  q.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_name LIKE '%geo%'")
  print('GEO TABLES',q.fetchall())
  q.execute('SELECT row_to_json(g) FROM g2p_geo_level_values g WHERE level_value_mnemonic IN (%s,%s,%s)',('Plateau','Jos North','Gangare'))
  print('GEO MATCHES',json.dumps(q.fetchall(),default=str))
  q.execute('SELECT row_to_json(g) FROM g2p_geo_levels g')
  print('LEVELS',json.dumps(q.fetchall(),default=str))
d=json.loads(subprocess.check_output(['kubectl','-n','nigeria','get','deploy','register-staff-portal-ui','-o','json']))
print('UI',json.dumps({'containers':[{k:v for k,v in x.items() if k in ['name','image','volumeMounts']} for x in d['spec']['template']['spec']['containers']], 'volumes':d['spec']['template']['spec'].get('volumes')}))
p=Path('/opt/openg2p-lab/odk-sync/receipts')/RID
if p.exists():
 print('RECEIPT', (p/'mapping.json').read_text())
