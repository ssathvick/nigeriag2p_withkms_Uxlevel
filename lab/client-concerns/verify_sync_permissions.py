import sys,json,requests
sys.path.insert(0,'/opt/openg2p-lab/odk-sync')
from odk_sync_worker import Client,ROOT,REG,FORM
client=Client(json.loads((ROOT/'config.json').read_text()))
try:
 denied=False
 try:client.post('/intake-form-data/approve_intake_form_submission',{'submission_id':'00000000-0000-4000-8000-000000000000','register_id':REG,'form_id':FORM})
 except requests.HTTPError as e:
  print('Sync identity approval endpoint:',e.response.status_code);denied=e.response.status_code==403
 assert denied,'Service must have no approval permission'
 # A project viewer may read the source but cannot create forms.
 response=client.odk.post(client.origin+'/v1/projects/1/forms',headers={'Content-Type':'application/xml'},data=b'<invalid/>',timeout=30)
 print('Source-reader form creation endpoint:',response.status_code);assert response.status_code==403
finally:client.close()
