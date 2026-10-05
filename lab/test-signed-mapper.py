import sys,subprocess,json,requests,base64,datetime
sys.path.insert(0,'/mnt/h/Nigeria_Mosip/codex/openg2p-lab')
from labdb import query
print('Key policies:',query('mosip_keymgr',"SELECT app_id FROM keymgr.key_policy_def;"))
def ip(service):return subprocess.check_output(['kubectl','get','svc',service,'-n','nigeria','-o','jsonpath={.spec.clusterIP}'],text=True).strip()
km='http://'+ip('commons-services-keymanager')+'/v1/keymanager'
now=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='milliseconds').replace('+00:00','Z')
r=requests.post(km+'/generateMasterKey/CERTIFICATE',json={'id':'nigeria-lab','version':'1.0','requesttime':now,'metadata':{},'request':{'applicationId':'OPENG2P_BRIDGE','referenceId':'','force':False}},timeout=30)
print('Generate signing key',r.status_code,'success' if r.json().get('response') else r.json().get('errors'))
certificate=r.json()['response']['certificate']
payload={'request_header':{'sender_app_mnemonic':'g2p_bridge','sender_app_url':'https://bridge.openg2p.localhost','request_id':'nigeria-lab-mapper-smoke','request_timestamp':now},'request_body':{'request_payload':{'transaction_id':'nigeria-lab-mapper-smoke','resolve_request':[{'reference_id':'nigeria-lab-1','timestamp':now,'id':'NG-LAB-0001','fa':'','scope':'details','locale':'en'}]}}}
data=base64.urlsafe_b64encode(json.dumps(payload,separators=(',',':'),sort_keys=True).encode()).decode().rstrip('=')
r=requests.post(km+'/jwtSign',json={'id':'nigeria-lab','version':'1.0','requesttime':now,'metadata':{},'request':{'applicationId':'OPENG2P_BRIDGE','referenceId':'','dataToSign':data,'includePayload':True,'includeCertificate':False,'includeCertHash':False}},timeout=30)
print('Sign mapper request',r.status_code,'success' if r.json().get('response') else r.json().get('errors'))
response=r.json().get('response')
if not response:raise RuntimeError('Keymanager signing failed')
signature=response['jwtSignedData']
header=json.loads(base64.urlsafe_b64decode(signature.split('.')[0]+'==='))
from cryptography import x509
from cryptography.hazmat.primitives import serialization
public_key=x509.load_pem_x509_certificate(certificate.encode()).public_key().public_bytes(serialization.Encoding.PEM,serialization.PublicFormat.SubjectPublicKeyInfo).decode()
q=lambda s:"'"+s.replace("'","''")+"'"
query('partner_management',"INSERT INTO pm_partners(id,partner_id,name,org_name,description,status,created_by,approved_by,created_at,updated_at) VALUES('nigeria-lab-bridge','PARTNER_G2P_BRIDGE','Nigeria Lab Bridge','OpenG2P local lab','Local synthetic payment test partner','active','nigeria-lab','nigeria-lab',now(),now()) ON CONFLICT(partner_id) DO NOTHING;")
query('partner_management',f"INSERT INTO pm_partner_keys(id,partner_id,kid,algorithm,public_key,status,created_at,updated_at) VALUES('nigeria-lab-bridge-key','PARTNER_G2P_BRIDGE',{q(header['kid'])},{q(header['alg'])},{q(public_key)},'active',now(),now()) ON CONFLICT(partner_id,kid) DO UPDATE SET public_key=EXCLUDED.public_key,status='active';")
r=requests.post('http://'+ip('spar-openg2p-spar-mapper-api')+'/mapper/resolve',json=payload,headers={'Signature':signature},timeout=30)
print('Signed mapper response',r.status_code,r.text[:1000])
r.raise_for_status()
assert r.json()['response_header']['response_status']!='ERROR',r.text
link_payload={'request_header':payload['request_header'],'request_body':{'request_payload':{'transaction_id':'nigeria-lab-link','link_request':[{'reference_id':'nigeria-lab-link-1','timestamp':now,'id':'NG-LAB-0001','name':'Fatima Abubakar','fa':{'strategy_id':5,'fa_type':'BANK','bank_name':'Example Bank Simulator','bank_code':'EXAMPLE','branch_name':'Local Test Branch','branch_code':'LAB','account_number':'LAB-000001'}}]}}}
def signed_call(path,body):
 data=base64.urlsafe_b64encode(json.dumps(body,separators=(',',':'),sort_keys=True).encode()).decode().rstrip('=')
 r=requests.post(km+'/jwtSign',json={'id':'nigeria-lab','version':'1.0','requesttime':now,'request':{'applicationId':'OPENG2P_BRIDGE','referenceId':'','dataToSign':data,'includePayload':True,'includeCertificate':False,'includeCertHash':False}},timeout=30)
 signature=r.json()['response']['jwtSignedData']
 r=requests.post('http://'+ip('spar-openg2p-spar-mapper-api')+path,json=body,headers={'Signature':signature},timeout=30)
 r.raise_for_status();print(path,r.text[:1100]);assert r.json()['response_header']['response_status']=='SUCCESS'
 return r.json()
signed_call('/mapper/link',link_payload)
resolved=signed_call('/mapper/resolve',payload)
assert resolved['response_body']['response_payload']['resolve_response'][0]['fa']
print('Signed link and account resolution succeeded with synthetic financial address.')



