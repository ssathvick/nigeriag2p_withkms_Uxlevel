from pathlib import Path
import ast,json,subprocess
from psycopg2.extras import RealDictCursor,Json
from psycopg2 import sql
from test_mbr_db_connection import connect
root=Path(__file__).parent;patch=root/'meeting-native/patched/register-staff-portal-api'
for group in ['models','schemas']:
 p=patch/'reference'/group/'individual.py';s=p.read_text();anchor='class G2P'+('Schema' if group=='schemas' else '')+'Individual:'
 if 'nin_confirmation:' not in s:s=s.replace(anchor,anchor+'\n    nin_confirmation: '+('Mapped[str] = mapped_column(String, nullable=True)' if group=='models' else 'Optional[str] = None')+'\n');ast.parse(s);p.write_text(s)
with connect() as c:
 with c.cursor(cursor_factory=RealDictCursor) as q:
  for t in ['g2p_intake_form_individuals','g2p_register_individuals','g2p_register_history_individuals']:q.execute(sql.SQL('ALTER TABLE {} ADD COLUMN IF NOT EXISTS nin_confirmation varchar').format(sql.Identifier(t)))
  q.execute("SELECT section_ui_schema FROM g2p_register_sections WHERE section_id='hh_members'");s=q.fetchone()['section_ui_schema'];cols=s['panels'][0]['widgets'][0]['widget-data-columns']
  if not any(x['column-key']=='nin_confirmation' for x in cols):cols.append({'widget':'text','column-key':'nin_confirmation','widget-label':'Confirm NIN / tracking number','widget-data-path':'nin_confirmation','widget-required':False})
  q.execute("UPDATE g2p_register_sections SET section_ui_schema=%s WHERE section_id='hh_members'",(Json(s),))
 c.commit()
run=lambda *a,input=None:subprocess.run(a,input=input,text=True,capture_output=True,check=True).stdout
cm=json.loads(run('kubectl','-n','nigeria','get','cm','native-household-parity','-o','json'));cm['data']['f2']=(patch/'reference/models/individual.py').read_text();cm['data']['f3']=(patch/'reference/schemas/individual.py').read_text();run('kubectl','replace','-f','-',input=json.dumps(cm))
for d in ['register-staff-portal-api','register-celery-worker','register-celery-beat-producer','register-partner-api','registry-bg-tasks-worker','registry-bg-tasks-producer','register-id-generator']:run('kubectl','-n','nigeria','rollout','restart','deploy/'+d)
p=patch/'openg2p_registry_core/services/intake_form_data_service.py';s=p.read_text();anchor='                year,month,day=member.get("birth_year"),member.get("birth_month"),member.get("birth_day")'
block='''                if member.get("nin_status") == "YES":
                    identification = member.get("foundational_id") if member.get("nin_id_type") == "NIN" else member.get("rid")
                    if str(member.get("nin_confirmation") or "").strip() != str(identification or "").strip():
                        self._invalid_request("The NIN or tracking number confirmation does not match.")
'''
if 'confirmation does not match' not in s:s=s.replace(anchor,block+anchor);ast.parse(s);p.write_text(s)
print('Added NIN/tracking confirmation without national ID authentication')
