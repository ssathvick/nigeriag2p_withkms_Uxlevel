"""Correct the SQL LIKE pattern for existing explicitly synthetic household programmes."""
import datetime as dt,json,sys
from pathlib import Path
sys.path.insert(0,'/opt/openg2p-lab/registration')
import registration_app as r
pb=r.Odoo('pbms-odoo','pbmsdb');backup=r.ROOT/'phase1-bank-backups'/dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ');backup.mkdir(parents=True,mode=0o700)
previous=[]
for p in r.rows("SELECT * FROM programs WHERE mnemonic LIKE 'IQS_INTEGRATED_%'"):
 for rule in pb.call('g2p.entitlement.rule.definition','search_read',[[['program_id','=',p['id']],['target_registry','=','household']]],{'fields':['pbms_domain']}):
  if rule['pbms_domain']=="[('link_registry_id','like','IQS-REG-HH-')]":
   previous.append(rule);pb.call('g2p.entitlement.rule.definition','write',[[rule['id']],{'pbms_domain':"[('link_registry_id','like','IQS-REG-HH-%')]"}])
(backup/'entitlement-rules-before.json').write_text(json.dumps(previous))
job=json.loads(Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/phase1-evidence/native-household-payment.json').read_text())
pb.call('g2p.beneficiary.list','write',[[job['listing_id']],{'entitlement_process_status':'pending'}])
print('Corrected',len(previous),'synthetic entitlement patterns and requested a native calculation retry.')
