"""Install the native addon into an existing, healthy PBMS 3 / Odoo 17 cluster.

Backs up the database and deployment. No fixture creation or bank dispatch.
Run with --help or without --apply to inspect the plan.
"""
import argparse,datetime,getpass,json,os,subprocess,time,xmlrpc.client
from pathlib import Path

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--apply',action='store_true');p.add_argument('--namespace',default='nigeria')
 p.add_argument('--deployment',default='pbms-odoo');p.add_argument('--database',default='pbmsdb')
 p.add_argument('--postgres-pod',default='pbms-postgresql-0')
 p.add_argument('--admin-login',default='admin@nigeria.openg2p.localhost')
 p.add_argument('--backup-root',type=Path,default=Path('/opt/openg2p-lab/pbms-react/backups'))
 a=p.parse_args();root=Path(__file__).resolve().parents[1];addon=root/'pbms-react/nsipa_approval'
 files={f.name:f.read_text() for f in addon.iterdir() if f.is_file() and f.suffix in {'.py','.xml','.csv'}}
 if not files:raise SystemExit('Native addon is missing')
 print(json.dumps({'namespace':a.namespace,'deployment':a.deployment,'database':a.database,'addon_files':sorted(files),'apply':a.apply}))
 if not a.apply:return
 import yaml
 def kube(*args,**kw):return subprocess.run(['kubectl','-n',a.namespace,*args],check=True,**kw)
 def read(*args):return subprocess.check_output(['kubectl','-n',a.namespace,*args],text=True)
 # Fail before mutation if the destination image lacks the XLS dependency.
 kube('exec','deployment/'+a.deployment,'--','python3','-c','import xlwt')
 dep=json.loads(read('get','deploy',a.deployment,'-o','json'))
 credentials=Path(os.environ.get('PBMS_CREDENTIALS_FILE','/opt/openg2p-lab/credentials.yaml'))
 password=os.environ.get('PBMS_ADMIN_PASSWORD')
 if not password and credentials.is_file():password=yaml.safe_load(credentials.read_text())['admin_password']
 if not password:password=getpass.getpass('Destination PBMS administrator password: ')
 ip=read('get','svc',a.deployment,'-o','jsonpath={.spec.clusterIP}').strip()
 url='http://'+ip;common=xmlrpc.client.ServerProxy(url+'/xmlrpc/2/common')
 uid=common.authenticate(a.database,a.admin_login,password,{})
 if not uid:raise SystemExit('PBMS administrator authentication failed; no changes applied')
 stamp=datetime.datetime.now().strftime('%Y%m%d-%H%M%S');backup=a.backup_root/('release-'+stamp);backup.mkdir(parents=True,mode=0o700)
 (backup/'deployment.json').write_text(json.dumps(dep))
 with (backup/'database.sql').open('wb') as output:
  kube('exec',a.postgres_pod,'--','bash','-c','export PGPASSWORD="$POSTGRES_POSTGRES_PASSWORD"; exec pg_dump -U postgres "$1"','nsipa-backup',a.database,stdout=output)
 (backup/'database.sql').chmod(0o600)
 cm={'apiVersion':'v1','kind':'ConfigMap','metadata':{'name':'nsipa-approval-addon','namespace':a.namespace},'data':files}
 kube('apply','-f','-',input=json.dumps(cm),text=True)
 spec=dep['spec']['template']['spec'];container=spec['containers'][0]
 spec['volumes']=[v for v in spec.get('volumes',[]) if v['name']!='nsipa-approval-addon']+[{'name':'nsipa-approval-addon','configMap':{'name':'nsipa-approval-addon'}}]
 container['volumeMounts']=[v for v in container.get('volumeMounts',[]) if v['name']!='nsipa-approval-addon']+[{'name':'nsipa-approval-addon','mountPath':'/opt/odoo/extraaddons/openg2p-pbms/nsipa_approval','readOnly':True}]
 dep['spec']['template'].setdefault('metadata',{}).setdefault('annotations',{})['nsipa-release']=stamp
 kube('replace','-f','-',input=json.dumps(dep),text=True)
 kube('rollout','status','deployment/'+a.deployment,'--timeout=240s')
 proxy=xmlrpc.client.ServerProxy(url+'/xmlrpc/2/object')
 def call(model,method,args):return proxy.execute_kw(a.database,uid,password,model,method,args)
 for attempt in range(20):
  try:call('ir.module.module','update_list',[]);break
  except (OSError,xmlrpc.client.ProtocolError):
   if attempt==19:raise
   time.sleep(2)
 ids=call('ir.module.module','search',[[['name','=','nsipa_approval']]])
 if len(ids)!=1:raise RuntimeError('Addon is not discoverable at the installed addons_path; restore deployment from '+str(backup))
 state=proxy.execute_kw(a.database,uid,password,'ir.module.module','read',[ids],{'fields':['state']})[0]['state']
 call('ir.module.module','button_immediate_upgrade' if state=='installed' else 'button_immediate_install',[ids])
 print('Native approval addon installed. Private recovery point: '+str(backup))

if __name__=='__main__':main()
