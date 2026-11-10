"""Supply the Redis client already installed in the matching bank worker image."""
import base64,datetime as dt,hashlib,json,subprocess,sys
from pathlib import Path
sys.path.insert(0,'/opt/openg2p-lab/registration')
import registration_app as r
script='''import redis,zipfile,io,base64
from pathlib import Path
p=Path(redis.__file__).parent;b=io.BytesIO()
with zipfile.ZipFile(b,'w',zipfile.ZIP_DEFLATED) as z:
 for f in p.rglob('*.py'):z.write(f,'redis/'+str(f.relative_to(p)))
 for metadata in p.parent.glob('redis-*.dist-info'):
  for f in metadata.rglob('*'):
   if f.is_file():z.write(f,str(f.relative_to(p.parent)))
print(base64.b64encode(b.getvalue()).decode())
'''
encoded=subprocess.check_output(['kubectl','-n','nigeria','exec','-i','deploy/openg2p-g2p-bridge-example-bank-celery','--','python','-'],input=script,text=True,stderr=subprocess.DEVNULL).strip()
if len(encoded)>900000:raise RuntimeError('Dependency bundle exceeds bounded ConfigMap size.')
bundle=base64.b64decode(encoded)
root=Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/compatibility');root.mkdir(exist_ok=True)
(root/'bank-api-redis-6.2.0.zip').write_bytes(bundle)
name='openg2p-g2p-bridge-example-bank-api'
deploy=json.loads(subprocess.check_output(['kubectl','-n','nigeria','get','deploy',name,'-o','json']))
backup=r.ROOT/'phase1-bank-backups'/dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ');backup.mkdir(parents=True,mode=0o700)
(backup/'bank-api-deployment.json').write_text(json.dumps(deploy));(backup/'bank-api-deployment.json').chmod(0o600)
cm={'apiVersion':'v1','kind':'ConfigMap','metadata':{'name':'phase1-bank-api-redis','namespace':'nigeria'},'binaryData':{'redis-runtime.zip':encoded}}
subprocess.run(['kubectl','apply','--server-side','--field-manager=phase1-runtime','-f','-'],input=json.dumps(cm),text=True,check=True,stdout=subprocess.DEVNULL)
s=deploy['spec']['template']['spec'];container=s['containers'][0]
s['volumes']=[v for v in s.get('volumes',[]) if v['name']!='phase1-bank-api-redis']+[{'name':'phase1-bank-api-redis','configMap':{'name':'phase1-bank-api-redis'}}]
mount='/opt/phase1-compat/redis-runtime.zip'
container['volumeMounts']=[v for v in container.get('volumeMounts',[]) if v['mountPath']!=mount]+[{'name':'phase1-bank-api-redis','mountPath':mount,'subPath':'redis-runtime.zip','readOnly':True}]
prior=next((v.get('value','') for v in container.get('env',[]) if v['name']=='PYTHONPATH'),'')
if mount not in prior:prior=mount+(':'+prior if prior else '')
container['env']=[v for v in container.get('env',[]) if v['name']!='PYTHONPATH']+[{'name':'PYTHONPATH','value':prior}]
deploy['spec']['template'].setdefault('metadata',{}).setdefault('annotations',{})['iqs-phase1-redis']=hashlib.sha256(bundle).hexdigest()
patched=subprocess.run(['kubectl','-n','nigeria','patch','deploy',name,'--type=merge','-p',json.dumps({'spec':{'template':deploy['spec']['template']}})],capture_output=True,text=True);patched.check_returncode()
subprocess.run(['kubectl','-n','nigeria','rollout','status','deploy/'+name,'--timeout=90s'],check=True)
print('Bank API now uses Redis 6.2.0 from its installed worker. Dependency checksum',hashlib.sha256(bundle).hexdigest())
