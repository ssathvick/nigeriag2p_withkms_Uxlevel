"""Link the six existing fictional payment beneficiaries using existing signing keys."""
import datetime as dt,json,subprocess,sys,base64,hashlib
from pathlib import Path
import requests
sys.path.insert(0,'/opt/openg2p-lab/registration')
import registration_app as r
with r.pg('bridge_db') as c:
 with c.cursor() as cur:
  cur.execute("SELECT DISTINCT beneficiary_id,beneficiary_name FROM disbursements WHERE beneficiary_id LIKE 'NG-LAB-%' ORDER BY beneficiary_id");people=cur.fetchall()
assert len(people)==6,'Expected the existing six native synthetic disbursements only'
now=dt.datetime.now(dt.timezone.utc).isoformat().replace('+00:00','Z')
body={'request_header':{'sender_app_mnemonic':'g2p_bridge','sender_app_url':'https://bridge.openg2p.localhost','request_id':'phase1-native-six-accounts','request_timestamp':now},'request_body':{'request_payload':{'transaction_id':'phase1-native-six-accounts','link_request':[{'reference_id':'phase1-link-'+ref,'timestamp':now,'id':ref,'name':name,'fa':{'strategy_id':5,'fa_type':'BANK','bank_name':'Local Example Bank Simulator','bank_code':'EXAMPLE','branch_name':'Synthetic branch','branch_code':'LAB','account_number':'LAB-'+ref.rsplit('-',1)[-1].zfill(6)}} for ref,name in people]}}}
encoded=base64.urlsafe_b64encode(json.dumps(body,separators=(',',':'),sort_keys=True).encode()).decode().rstrip('=')
sign=requests.post(r.svc('commons-services-keymanager')+'/v1/keymanager/jwtSign',json={'id':'phase1-sandbox','version':'1.0','requesttime':now,'request':{'applicationId':'OPENG2P_BRIDGE','referenceId':'','dataToSign':encoded,'includePayload':True,'includeCertificate':False,'includeCertHash':False}},timeout=20);sign.raise_for_status()
signature=sign.json()['response']['jwtSignedData']
response=requests.post(r.svc('spar-openg2p-spar-mapper-api')+'/mapper/link',json=body,headers={'Signature':signature},timeout=20);response.raise_for_status();data=response.json()
assert data['response_header']['response_status']=='SUCCESS','Signed linking failed'
print('Existing signed SPAR linkage verified for six fictional native beneficiaries. No new signing keys.')

# Strict resolution: a batch with unresolved beneficiaries must not dispatch.
deploy='bridge-celery-worker';path='/usr/local/lib/python3.12/site-packages/openg2p_g2p_bridge_celery_workers/tasks/mapper_resolution_task.py'
source=subprocess.check_output(['kubectl','-n','nigeria','exec','deploy/'+deploy,'--','cat',path],text=True)
marker='            # batch_has_error = True'
if marker not in source and '            batch_has_error = True' not in source:raise RuntimeError('Unexpected installed mapper implementation; inspect before patching.')
patched=source.replace(marker,'            batch_has_error = True')
patched=patched.replace('    batch_has_error = False','    resolved_ids = {item.id for item in resolve_response.results if item.fa}\n    batch_has_error = bool(set(beneficiary_disbursement_map) - resolved_ids)')
backup=r.ROOT/'phase1-bank-backups'/dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ');backup.mkdir(parents=True,mode=0o700)
(backup/'mapper_resolution_task.py').write_text(source)
old=json.loads(subprocess.check_output(['kubectl','-n','nigeria','get','deploy',deploy,'-o','json']))
(backup/'deployment.json').write_text(json.dumps(old));(backup/'deployment.json').chmod(0o600)
cm={'apiVersion':'v1','kind':'ConfigMap','metadata':{'name':'phase1-strict-mapper','namespace':'nigeria'},'data':{'mapper_resolution_task.py':patched}}
subprocess.run(['kubectl','apply','-f','-'],input=json.dumps(cm),text=True,check=True,stdout=subprocess.DEVNULL)
spec=old['spec']['template']['spec'];container=spec['containers'][0]
old['spec']['template'].setdefault('metadata',{}).setdefault('annotations',{})['iqs-phase1-mapper-version']=hashlib.sha256(patched.encode()).hexdigest()
spec['volumes']=[v for v in spec.get('volumes',[]) if v['name']!='phase1-strict-mapper']+[{'name':'phase1-strict-mapper','configMap':{'name':'phase1-strict-mapper'}}]
container['volumeMounts']=[m for m in container.get('volumeMounts',[]) if m['mountPath']!=path]+[{'name':'phase1-strict-mapper','mountPath':path,'subPath':'mapper_resolution_task.py','readOnly':True}]
patch=subprocess.run(['kubectl','-n','nigeria','patch','deploy',deploy,'--type=merge','-p',json.dumps({'spec':{'template':old['spec']['template']}})],capture_output=True,text=True)
patch.check_returncode()
subprocess.run(['kubectl','-n','nigeria','rollout','status','deploy/'+deploy,'--timeout=90s'],check=True)
print('Strict native mapping guard deployed; unresolved beneficiaries block bank dispatch. Backup retained privately.')
