import pathlib,json
exec(pathlib.Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/seed-platform-batch.py').read_text().split("query('register','BEGIN;")[0])
result={}
for service,db in [('registry-odoo','socialregistrydb'),('portal-backend-odoo','portalpbmsdb')]:
 o=Odoo(service,db)
 individuals=o.call('res.partner','search_count',[[['ref','like',tag+'-I-%']]])
 households=o.call('res.partner','search_count',[[['ref','like',tag+'-HH-%']]])
 assert (individuals,households)==(200,50)
 result[db]={'individuals':individuals,'households':households}
p=Odoo('pbms-odoo','pbmsdb')
count=p.call('g2p.farmer.registry','search_count',[[['link_registry_id','like',tag+'%']]])
assert count==200
result['pbms_fixture_rows']=count
o=Odoo('portal-backend-odoo','portalpbmsdb')
apps=o.call('g2p.program.registrant_info','search_count',[[['application_id','>=','91003000000'],['application_id','<','91004000000']]])
assert apps==205
result['linked_applications']=apps
result['verified']=True
(workspace/'synthetic-data/verification.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result))
