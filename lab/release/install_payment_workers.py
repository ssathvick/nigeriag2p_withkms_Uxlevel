"""Plan/install version-checked PBMS payment worker extensions; never dispatch payments."""
import argparse,datetime,hashlib,json,subprocess
from pathlib import Path

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--apply',action='store_true');p.add_argument('--namespace',default='nigeria');p.add_argument('--deployment',default='pbms-celery-worker')
 p.add_argument('--backup-root',type=Path,default=Path('/opt/openg2p-lab/pbms-react/backups'))
 a=p.parse_args();source=Path(__file__).resolve().parents[1]/'pbms-react'
 tasks='/usr/local/lib/python3.12/site-packages/openg2p_bg_task_celery_workers/tasks/'
 files={'nsipa_payment_snapshot.py':'nsipa_payment_snapshot.py','disbursement_envelope_creation_worker.py':'nsipa_disbursement_envelope_worker.py','disbursement_batch_creation_worker.py':'nsipa_disbursement_batch_worker.py'}
 data={k:(source/v).read_text(encoding='utf-8-sig') for k,v in files.items()}
 for k,v in data.items():compile(v,k,'exec')
 print(json.dumps({'namespace':a.namespace,'deployment':a.deployment,'files':list(data),'apply':a.apply,'dispatches_payments':False}))
 if not a.apply:return
 def kube(*args,**kw):return subprocess.run(['kubectl','-n',a.namespace,*args],check=True,**kw)
 def read(*args):return subprocess.check_output(['kubectl','-n',a.namespace,*args],text=True)
 dep=json.loads(read('get','deploy',a.deployment,'-o','json'))
 # Fail before mutation if upstream worker versions differ from this release.
 for name in files:
  if name=='nsipa_payment_snapshot.py':continue
  reference=source/'backend-reference'/('openg2p_bg_task_celery_workers__tasks__'+name)
  live=read('exec','deploy/'+a.deployment,'--','cat',tasks+name)
  normalize=lambda s:s.lstrip('\ufeff').replace('\r\n','\n').rstrip()+'\n'
  if normalize(live) not in {normalize(reference.read_text()),normalize(data[name])}:
   raise SystemExit('Unsupported worker source: '+name+'. Review the destination version before installing.')
 stamp=datetime.datetime.now().strftime('%Y%m%d-%H%M%S');backup=a.backup_root/('payment-workers-'+stamp);backup.mkdir(parents=True,mode=0o700)
 (backup/'deployment.json').write_text(json.dumps(dep))
 previous=subprocess.run(['kubectl','-n',a.namespace,'get','cm','nsipa-payment-workers','-o','json'],capture_output=True,text=True)
 if previous.returncode==0:(backup/'configmap.json').write_text(previous.stdout)
 cm={'apiVersion':'v1','kind':'ConfigMap','metadata':{'name':'nsipa-payment-workers','namespace':a.namespace},'data':data}
 kube('apply','-f','-',input=json.dumps(cm),text=True)
 spec=dep['spec']['template']['spec'];container=spec['containers'][0]
 spec['volumes']=[v for v in spec.get('volumes',[]) if v['name']!='nsipa-payment-workers']+[{'name':'nsipa-payment-workers','configMap':{'name':'nsipa-payment-workers'}}]
 container['volumeMounts']=[v for v in container.get('volumeMounts',[]) if v['name']!='nsipa-payment-workers']+[{'name':'nsipa-payment-workers','mountPath':tasks+name,'subPath':name,'readOnly':True} for name in files]
 patch={'spec':{'template':{'metadata':{'annotations':{'nsipa-payment-release':stamp}},'spec':{'volumes':spec['volumes'],'containers':spec['containers']}}}}
 kube('patch','deploy',a.deployment,'--type=merge','-p',json.dumps(patch))
 kube('rollout','status','deploy/'+a.deployment,'--timeout=180s')
 print('Payment worker extensions installed. Recovery deployment: '+str(backup/'deployment.json'))

if __name__=='__main__':main()
