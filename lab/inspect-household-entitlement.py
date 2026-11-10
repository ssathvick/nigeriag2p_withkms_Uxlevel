import json,sys
from pathlib import Path
sys.path.insert(0,'/opt/openg2p-lab/registration')
import registration_app as r
job=json.loads(Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/phase1-evidence/native-household-payment.json').read_text())
p=r.Odoo('pbms-odoo','pbmsdb')
print('Entitlement rules',p.call('g2p.entitlement.rule.definition','search_read',[[['program_id','=',job['program_id']]]],{'fields':['mnemonic','quantity','pbms_domain','target_registry','benefit_code_id']}))
print('Sandbox programme',r.one('SELECT mnemonic,amount,max_income,min_members FROM programs WHERE id=?',(job['program_id'],)))
with r.pg('bgtaskdb','pbms-postgresql') as c:
 with c.cursor() as cur:
  cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name='beneficiary_list_details'");print('Job detail columns',[x[0] for x in cur.fetchall()])
