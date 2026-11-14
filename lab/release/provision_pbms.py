"""Create fresh demonstration staff identities and/or grant programme access.

Existing passwords are preserved. New passwords go only to a private output file.
"""
import argparse,getpass,json,os,secrets,subprocess,xmlrpc.client
from pathlib import Path

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--apply',action='store_true');p.add_argument('--namespace',default='nigeria')
 p.add_argument('--accounts',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
 p.add_argument('--programme-id',type=int);p.add_argument('--admin-login',default='admin@nigeria.openg2p.localhost')
 a=p.parse_args();roles=json.loads(a.accounts.read_text());mapping={'Programme Admin':'admin','Payment':'payment','Finance':'finance','Audit':'audit','CEO':'ceo'}
 if set(roles)!=set(mapping) or len(set(roles.values()))!=5:p.error('Supply five distinct logins, keyed by Programme Admin, Payment, Finance, Audit and CEO')
 if a.output.exists():p.error('Output already exists; use a new private filename. Existing account passwords will still be preserved')
 print(json.dumps({'accounts':len(roles),'programme_id':a.programme_id,'apply':a.apply}))
 if not a.apply:return
 import yaml
 path=Path(os.environ.get('PBMS_CREDENTIALS_FILE','/opt/openg2p-lab/credentials.yaml'))
 password=os.environ.get('PBMS_ADMIN_PASSWORD') or (yaml.safe_load(path.read_text())['admin_password'] if path.is_file() else getpass.getpass('PBMS administrator password: '))
 host=subprocess.check_output(['kubectl','-n',a.namespace,'get','svc','pbms-odoo','-o','jsonpath={.spec.clusterIP}'],text=True).strip();url='http://'+host
 uid=xmlrpc.client.ServerProxy(url+'/xmlrpc/2/common').authenticate('pbmsdb',a.admin_login,password,{})
 if not uid:raise SystemExit('PBMS authentication failed')
 proxy=xmlrpc.client.ServerProxy(url+'/xmlrpc/2/object')
 def call(m,f,args,kw=None):return proxy.execute_kw('pbmsdb',uid,password,m,f,args,kw or {})
 def ref(module,name):return call('ir.model.data','search_read',[[['module','=',module],['name','=',name]]],{'fields':['res_id']})[0]['res_id']
 # Create the private result with exclusive mode before provisioning; fsync after each account.
 a.output.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
 fd=os.open(a.output,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
 results={}
 with os.fdopen(fd,'w') as stream:
  for role,login in roles.items():
   found=call('res.users','search',[[['login','=',login]]],{'context':{'active_test':False}})
   group=ref('nsipa_approval','group_'+mapping[role])
   if found:
    user=call('res.users','read',[found],{'fields':['active','share']})[0]
    if not user['active'] or user['share']:raise RuntimeError('Existing account must be an active internal user: '+login)
    ident=found[0];call('res.users','write',[[ident],{'groups_id':[[4,group]]}]);entry={'login':login,'uid':ident,'password_preserved':True}
   else:
    temporary=secrets.token_urlsafe(24)
    ident=call('res.users','create',[{'name':role,'login':login,'password':temporary,'groups_id':[[6,0,[ref('base','group_user'),group]]]}])
    entry={'login':login,'uid':ident,'password':temporary}
   if a.programme_id:call('g2p.program.definition','nsipa_assign_role',[[a.programme_id],ident,role])
   results[role]=entry;stream.seek(0);json.dump(results,stream,indent=2);stream.truncate();stream.flush();os.fsync(stream.fileno())
 print('Accounts configured; private results saved. No passwords printed.')

if __name__=='__main__':main()
