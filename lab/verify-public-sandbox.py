import json,subprocess,requests,pathlib,yaml
R=pathlib.Path('/opt/openg2p-lab');password=yaml.safe_load((R/'credentials.yaml').read_text())['admin_password']
report=[]
for host,db in [('pbms','pbmsdb'),('registry','socialregistrydb'),('portal-admin','portalpbmsdb')]:
 s=requests.Session();u='https://'+host+'.nigeriag2p.com'
 r=s.post(u+'/web/session/authenticate',json={'jsonrpc':'2.0','params':{'db':db,'login':'admin@nigeria.openg2p.localhost','password':password},'id':1},timeout=25)
 r.raise_for_status();ok=bool(r.json().get('result',{}).get('uid'))
 report.append({'service':host,'login':ok,'HTTPS':r.headers.get('server')=='cloudflare'})
 if not ok:raise RuntimeError(host+' authentication failed')
for path in ['/admin/','/realms/master/']:
 r=requests.get('https://keycloak.nigeriag2p.com'+path,timeout=15);assert r.status_code==404
for h in ['pbms','registry','portal-admin']:
 r=requests.get('https://'+h+'.nigeriag2p.com/web/database/manager',timeout=15);assert r.status_code==404
items=json.loads(subprocess.check_output(['kubectl','-n','nigeria','get','deploy,sts','-o','json']))['items']
not_ready=[o['metadata']['name'] for o in items if o.get('status',{}).get('readyReplicas',0)<o['spec'].get('replicas',1)]
result={'domain':'nigeriag2p.com','odoo_checks':report,'private_admin_paths_blocked':True,'not_ready':not_ready,'tunnel':subprocess.check_output(['systemctl','is-active','cloudflared'],text=True).strip()}
(R/'public-verification.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
