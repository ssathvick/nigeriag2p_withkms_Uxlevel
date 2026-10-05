import pathlib,json
source=pathlib.Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/seed-platform-batch.py').read_text()
exec(source.split("query('register','BEGIN;")[0])
portal=Odoo('portal-backend-odoo','portalpbmsdb')
partners=portal.call('res.partner','search',[[['ref','like',tag+'-I-%']]])
fatima=portal.call('res.partner','search',[[['ref','=','NG-PORTAL-0001']]])[0]
programs=[r['id'] for r in portal.call('g2p.program','search_read',[[]],{'fields':['name']}) if 'IQS Synthetic Demo' in r['name']]
members=portal.call('g2p.program_membership','search_read',[[['partner_id','in',partners+[fatima]],['program_id','in',programs]]],{'fields':['partner_id','program_id','state']})
print('Selected',len(partners),programs,len(members),portal.call('g2p.program','search_read',[[]],{'fields':['name']}),flush=True)
states=['active','inprogress','rejected','completed','closed']
for i,m in enumerate(members):
 app=str(91003000000+m['id'])
 existing=portal.call('g2p.program.registrant_info','search',[[['program_membership_id','=',m['id']]]])
 if len(existing)>1:
  portal.call('g2p.program.registrant_info','unlink',[existing[1:]])
  existing=existing[:1]
 if not existing:
  existing=[portal.call('g2p.program.registrant_info','create',[{'registrant_id':m['partner_id'][0],'program_id':m['program_id'][0],'program_membership_id':m['id'],'state':states[i%5],'program_registrant_info':{'contactName':m['partner_id'][1],'supportRequest':'Synthetic local UX application','demoConsent':True}}])]
 portal.call('g2p.program.registrant_info','write',[existing,{'application_id':app,'state':states[i%5]}])
count=portal.call('g2p.program.registrant_info','search_count',[[['program_membership_id','in',[m['id'] for m in members]]]])
assert count==205,count
print('Verified 205 linked beneficiary applications, including five for Fatima.')
for path in [workspace/'synthetic-data/summary.json',root/'synthetic-platform-batch.json']:
 data=json.loads(path.read_text())
 target=data.get('report',data)
 if 'beneficiary_portal' in target:target['beneficiary_portal']['linked_applications']=count
 path.write_text(json.dumps(data,indent=2))
