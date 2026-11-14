"""Deploy the supplied vector identity without changing workflow or application data."""
from pathlib import Path
import base64,datetime,hashlib,json,re,shutil,subprocess,xmlrpc.client
import requests,yaml

source=Path(__file__).parent;root=Path('/opt/openg2p-lab')
backup=root/'logo-replacement-backups'/datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
backup.mkdir(parents=True,mode=0o700);manifest=[];companies=[]
version='supplied-'+hashlib.sha256((source/'branding/nsipa-logo.svg').read_bytes()).hexdigest()[:12]
def install(src,target):
 target=Path(target);saved=backup/('file-'+str(len(manifest)))
 if target.exists():shutil.copy2(target,saved)
 manifest.append({'target':str(target),'saved':str(saved) if saved.exists() else None})
 target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,target)
def change(target,text):
 temp=backup/('candidate-'+str(len(manifest)));temp.write_text(text);install(temp,target)
css='''
/* Supplied user vector logo: complete mark, aspect ratio preserved. */
.iqs-brand-logo{width:86px!important;height:62px!important;max-width:160px!important;max-height:100px!important;object-fit:contain!important}
.iqs-logo-mark{width:190px!important;height:145px!important;margin:0 auto 16px}
.nsipa-nav-logo{width:86px!important;height:62px!important;object-fit:contain!important}
#ng2p-platform-bar .nsipa-nav-logo{width:58px!important;height:44px!important}
.wordmark .nsipa-nav-logo{width:100px!important;height:76px!important}
.brand img[src*="nsipa-"]{width:80px!important;height:60px!important;object-fit:contain!important}
.dash-brand img,.jc-brand img,.ti-brand img{width:78px!important;height:58px!important;object-fit:contain!important}
.iqs-login .powered-by .iqs-brand-logo{width:60px!important;height:44px!important}
.nsipa-service-logo{width:52px!important;height:40px!important;object-fit:contain!important}
@media(max-width:600px){.nsipa-nav-logo{width:74px!important;height:54px!important}.iqs-logo-mark{height:125px}}
@media(max-width:600px){#ng2p-platform-bar{gap:8px!important;padding:8px 10px!important;justify-content:space-between!important;flex-wrap:nowrap!important}#ng2p-platform-bar>.ng2p-platform-module,#ng2p-platform-bar>a:nth-of-type(3){display:none!important}#ng2p-platform-bar>a,#ng2p-platform-bar>button{font-size:11px!important;white-space:nowrap!important}#ng2p-platform-bar .ng2p-platform-brand{flex:0 0 58px!important}}
'''
def service(name):return 'http://'+subprocess.check_output(['kubectl','-n','nigeria','get','svc',name,'-o','jsonpath={.spec.clusterIP}'],text=True).strip()
try:
 for name in ['nsipa-logo.svg','nsipa-wordmark.svg','nsipa-symbol.svg','nsipa-logo.png','iqs-logo.png','nsipa-original-supplied.svg','replacement-logo-source.json']:
  install(source/'branding'/name,root/'branding'/name)
 for p in [source/'branding/iqs-brand.css',root/'branding/iqs-brand.css']:
  text=p.read_text()
  marker='/* Supplied user vector logo: complete mark, aspect ratio preserved. */'
  if marker in text:text=text[:text.index(marker)]
  if p==source/'branding/iqs-brand.css':p.write_text(text+css)
  else:change(p,text+css)
 # Keep current shared-script fixes, changing only logo asset cache keys.
 for p in [source/'branding/iqs-brand.js',root/'branding/iqs-brand.js']:
  text=p.read_text()
  for name in ['nsipa-logo.svg','nsipa-wordmark.svg','nsipa-symbol.svg']:
   text=re.sub(re.escape(name)+r'(?:\?v=[a-zA-Z0-9_-]+)?',name+'?v='+version,text)
  if p==source/'branding/iqs-brand.js':p.write_text(text)
  else:change(p,text)
 for name in ['mbr.js','mbr.css']:install(source/'persona-ui/dist'/name,root/'registration/static'/name)
 for name in ['phase1-public.html','jos-connected.html']:
  path=root/'registration/templates'/name;text=path.read_text()
  text=text.replace('<a class="brand" href="/">NSIPA</a>','<a class="brand" href="/"><img src="/iqs-brand/nsipa-logo.svg?v='+version+'" alt="NSIPA"/></a>')
  text=text.replace('<a class="jc-brand" href="/jos-cct/">NSIPA / JOS CCT</a>','<a class="jc-brand" href="/jos-cct/"><img src="/iqs-brand/nsipa-logo.svg?v='+version+'" alt="NSIPA"/><span>Jos CCT</span></a>')
  change(path,text)
 # Replace only PBMS compiled UI assets in the active release.
 pbms=(root/'pbms-react/current').resolve()
 if not str(pbms).startswith(str(root/'pbms-react/releases')+'/'):raise RuntimeError('Unexpected PBMS release target')
 for name in ['app.js','app.css']:install(source/'pbms-react/dist'/name,pbms/name)
 # Public atlas and pilot use the same asset; keep standalone header sizes legible.
 for folder in ['territories','jos-cct']:
  for csspath in (root/'public-home'/folder).glob('*.css'):
   text=csspath.read_text();marker='/* Supplied logo sizing */'
   if marker not in text:change(csspath,text+'\n'+marker+'\n.ti-brand img,.jc-brand img{width:76px!important;height:56px!important;object-fit:contain!important}\n')
 # Invalidate shared CSS/script URLs in every injected service, preserving all routes.
 snippet=Path('/etc/nginx/snippets/iqs-brand.conf');text=snippet.read_text()
 for name in ['iqs-brand.css','iqs-brand.js']:
  text=re.sub(re.escape('/iqs-brand/'+name)+r'(?:\?[^"\s]*)?', '/iqs-brand/'+name+'?v='+version,text)
 change(snippet,text)
 subprocess.run(['nginx','-t'],check=True,capture_output=True)
 subprocess.run(['systemctl','reload','nginx'],check=True)
 subprocess.run(['systemctl','restart','iqs-registration'],check=True)
 # Native Odoo company logos cover server-rendered pages, reports and emails.
 password=yaml.safe_load((root/'credentials.yaml').read_text())['admin_password']
 png=base64.b64encode((source/'branding/nsipa-logo.png').read_bytes()).decode()
 for name,database in [('pbms-odoo','pbmsdb'),('registry-odoo','socialregistrydb'),('portal-backend-odoo','portalpbmsdb')]:
  url=service(name);uid=xmlrpc.client.ServerProxy(url+'/xmlrpc/2/common').authenticate(database,'admin@nigeria.openg2p.localhost',password,{})
  if not uid:raise RuntimeError('Native branding authentication failed: '+name)
  proxy=xmlrpc.client.ServerProxy(url+'/xmlrpc/2/object',allow_none=True)
  def call(method,args):return proxy.execute_kw(database,uid,password,'res.company',method,args)
  ids=call('search',[[]]);old=call('read',[ids,['logo']])
  saved=backup/(name+'-company-logos.json');saved.write_text(json.dumps(old));saved.chmod(0o600)
  companies.append({'service':name,'database':database,'saved':str(saved)})
  call('write',[ids,{'logo':png}])
 (backup/'manifest.json').write_text(json.dumps({'files':manifest,'companies':companies,'version':version},indent=2))
 # Same-origin logo responses across the integrated application and native services.
 hosts=['g2p.wverve.in','g2p-register.wverve.in','g2p-pbms.wverve.in','g2p-registry.wverve.in','g2p-keycloak.wverve.in','g2p-beneficiary.wverve.in','g2p-awe.wverve.in','g2p-odk.wverve.in','g2p-master-data-ui.wverve.in','g2p-consent-manager.wverve.in','g2p-partner-management.wverve.in','g2p-staff-portal.wverve.in','g2p-superset.wverve.in']
 checks=[]
 for host in hosts:
  for name in ['nsipa-logo.svg','nsipa-wordmark.svg','nsipa-symbol.svg']:
   response=requests.get('http://127.0.0.1:18080/iqs-brand/'+name,headers={'Host':host,'Connection':'close'},timeout=20)
   valid=response.status_code==200 and response.content==(source/'branding'/name).read_bytes()
   checks.append({'host':host,'asset':name,'passed':valid})
 if not all(x['passed'] for x in checks):raise RuntimeError('A shared logo asset did not verify')
 report={'status':'deployed','version':version,'backup':str(backup),'asset_checks':checks,'native_services':[x['service'] for x in companies]}
 output=source.parent/'output/logo-replacement';output.mkdir(parents=True,exist_ok=True)
 (output/'deployment-verification.json').write_text(json.dumps(report,indent=2))
 print(json.dumps({'status':'deployed','asset_checks':len(checks),'native_services':report['native_services'],'backup':str(backup)}))
except Exception:
 for entry in reversed(manifest):
  if entry['saved']:shutil.copy2(entry['saved'],entry['target'])
  elif Path(entry['target']).exists():Path(entry['target']).unlink()
 for company in companies:
  url=service(company['service']);database=company['database'];uid=xmlrpc.client.ServerProxy(url+'/xmlrpc/2/common').authenticate(database,'admin@nigeria.openg2p.localhost',password,{})
  proxy=xmlrpc.client.ServerProxy(url+'/xmlrpc/2/object',allow_none=True)
  for item in json.loads(Path(company['saved']).read_text()):proxy.execute_kw(database,uid,password,'res.company','write',[[item['id']],{'logo':item['logo']}])
 subprocess.run(['nginx','-t'],check=True,capture_output=True);subprocess.run(['systemctl','reload','nginx'],check=True)
 raise
