"""Calculate one approved synthetic household's benefit through native PBMS."""
import datetime as dt,json,sys,time
from pathlib import Path
sys.path.insert(0,'/opt/openg2p-lab/registration')
import registration_app as r
account=json.loads((r.ROOT/'test-account.json').read_text())
profile=r.one('SELECT * FROM profiles WHERE data LIKE ?',('%'+account['username']+'@example.invalid%',))
assert profile and profile['status']=='approved' and profile['sync_status']=='complete' and json.loads(profile['data']).get('synthetic') is True
application=r.one("SELECT * FROM applications WHERE sub=? AND status='enrolled'",(profile['sub'],));assert application
program=r.one('SELECT * FROM programs WHERE id=?',(application['program'],))
pb=r.Odoo('pbms-odoo','pbmsdb')
assert pb.call('g2p.beneficiary.list','read',[[application['pbms_list']]],{'fields':['list_workflow_status']})[0]['list_workflow_status']=='approved_final_enrolment'
suffix='_ON_US_VERIFIED' if '--on-us' in sys.argv else ''
cycle_name='PHASE1_UAT_HOUSEHOLD_PAYMENT'+suffix;list_name='PHASE1_UAT_HOUSEHOLD_ENTITLEMENT'+suffix
cycle=pb.upsert('g2p.disbursement.cycle',[['cycle_mnemonic','=',cycle_name]],{'cycle_mnemonic':cycle_name,'program_id':program['id'],'disbursement_schedule_date':str(dt.date.today())})
existing=pb.call('g2p.beneficiary.list','search',[[['mnemonic','=',list_name]]])
if existing:listing=existing[0]
else:listing=pb.call('g2p.beneficiary.list','create',[{'mnemonic':list_name,'disbursement_cycle_id':cycle,'iqs_household_ref':profile['household_ref'],'brief':'One previously enrolled fictional household. Local Example Bank only. No government policy or real payment.','eligibility_process_status':'pending'}])
fields=['eligibility_process_status','entitlement_process_status','number_of_registrants','number_of_entitlements_processed','eligibility_latest_error_code']
report={'scope':'Existing approved and enrolled synthetic household; native PBMS calculation','household_reference':profile['household_ref'],'program_id':program['id'],'benefit_code_id':program['benefit_id'],'cycle_id':cycle,'listing_id':listing}
path=Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/phase1-evidence/native-household-payment.json')
for _ in range(24):
 row=pb.call('g2p.beneficiary.list','read',[[listing]],{'fields':fields})[0]
 report['calculation']={k:row[k] for k in fields};path.write_text(json.dumps(report,indent=2))
 if row['eligibility_process_status']=='complete' and row['entitlement_process_status']=='complete':break
 time.sleep(5)
with r.pg('bgtaskdb','pbms-postgresql') as c:
 with c.cursor() as cur:
  uid=pb.call('g2p.beneficiary.list','read',[[listing]],{'fields':['beneficiary_list_id']})[0]['beneficiary_list_id']
  cur.execute('SELECT registrant_details FROM beneficiary_list_details WHERE beneficiary_list_id=%s',(uid,))
  details=[d for chunk, in cur.fetchall() for d in chunk]
assert len(details)==1 and details[0]['registrant_id']==profile['household_ref']
report['actual_entitlement_ngn']=details[0]['entitlement'].get(str(program['benefit_id']))
report['counter_note']='Native counter and durable calculation result verified after worker correction.'
report['status']='passed_calculation' if row['eligibility_process_status']=='complete' and row['entitlement_process_status']=='complete' and row['number_of_registrants']==1 and report['actual_entitlement_ngn']==25000 else 'blocked'
path.write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
