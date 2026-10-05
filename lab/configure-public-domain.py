"""Configure the existing synthetic lab for a stable public domain, keeping local routes."""
import json, subprocess, pathlib, shutil, re, requests, yaml, os
ROOT=pathlib.Path('/opt/openg2p-lab')
DOMAIN='nigeriag2p.com'
def run(args, **kw): return subprocess.run(args,check=True,**kw)
def get(kind,ns='nigeria'): return json.loads(subprocess.check_output(['kubectl','-n',ns,'get',kind,'-o','json']))['items']
def patch(kind,name,body,ns='nigeria'):
 run(['kubectl','-n',ns,'patch',kind,name,'--type=merge','-p',json.dumps(body)],stdout=subprocess.DEVNULL)
def convert(s):
 return s.replace('beneficiary.openg2p-ux.localhost','beneficiary.'+DOMAIN).replace('.openg2p.localhost','.'+DOMAIN).replace('https://openg2p.localhost','https://'+DOMAIN)
snapshot=ROOT/'public-domain-backup'
if not snapshot.exists():
 snapshot.mkdir(mode=0o700)
 for kind in ['deploy','sts','cm','virtualservice','gateway']:
  (snapshot/(kind+'.json')).write_bytes(subprocess.check_output(['kubectl','-n','nigeria','get',kind,'-o','json']))
 shutil.copy('/etc/nginx/sites-available/openg2p-lab',snapshot/'nginx.conf')
 shutil.copy(ROOT/'tls/server.crt',snapshot/'server.crt')
 shutil.copy(ROOT/'tls/server.key',snapshot/'server.key')
 run(['chmod','-R','go-rwx',str(snapshot)])
hosts={DOMAIN}
for obj in get('virtualservice'):
 spec=obj['spec']; old=spec['hosts']; spec['hosts']=list(dict.fromkeys(old+[convert(h) for h in old]))
 for route in spec.get('http',[]):
  route.get('headers',{}).get('request',{}).get('set',{}).pop('x-forwarded-host',None)
 hosts.update(spec['hosts']); patch('virtualservice',obj['metadata']['name'],{'spec':spec})
for gateway in get('gateway'):
 for server in gateway['spec']['servers']:
  server['hosts']=list(dict.fromkeys(server['hosts']+[convert(h) for h in server['hosts']]))
 patch('gateway',gateway['metadata']['name'],{'spec':gateway['spec']})
ip=subprocess.check_output(['hostname','-I'],text=True).split()[0]
# A locally trusted certificate also serves pod-to-pod HTTPS requests for public names.
ext=ROOT/'tls/public-extensions'
ext.write_text('subjectAltName=DNS:openg2p.localhost,DNS:*.openg2p.localhost,DNS:beneficiary.openg2p-ux.localhost,DNS:'+DOMAIN+',DNS:*.'+DOMAIN+'\nextendedKeyUsage=serverAuth\n')
run(['openssl','x509','-req','-in',str(ROOT/'tls/server.csr'),'-CA',str(ROOT/'tls/ca.crt'),'-CAkey',str(ROOT/'tls/ca.key'),'-CAcreateserial','-out',str(ROOT/'tls/server.crt'),'-days','825','-extfile',str(ext)],stderr=subprocess.DEVNULL)
for obj in get('cm'):
 data=obj.get('data',{}); changed=False
 for key,value in data.items():
  new=convert(value)
  if new!=value: data[key]=new; changed=True
 if changed:patch('cm',obj['metadata']['name'],{'data':data})
for kind in ['deployment','statefulset']:
 for obj in get(kind):
  spec=obj['spec']['template']['spec']
  spec['hostAliases']=[{'ip':ip,'hostnames':sorted(hosts)}]
  for c in spec.get('containers',[])+spec.get('initContainers',[]):
   for e in c.get('env',[]):
    if 'value' in e and e['name'] not in ['ODOO_EMAIL','SYSADMIN_EMAIL','EMAIL_FROM']:
     e['value']=convert(e['value'])
   # ConfigMap-backed applications need restarting after configuration changes.
  patch(kind,obj['metadata']['name'],{'spec':{'template':{'metadata':{'annotations':{'iqs.public-domain':DOMAIN}},'spec':spec}}})
core=get('cm','kube-system')
core=next(o for o in core if o['metadata']['name']=='coredns')
lines=[l for l in core['data'].get('NodeHosts','').splitlines() if DOMAIN not in l and 'openg2p.localhost' not in l and 'openg2p-ux.localhost' not in l]
lines.extend(ip+' '+h for h in sorted(hosts))
patch('cm','coredns',{'data':{'NodeHosts':'\n'.join(lines)+'\n'}},'kube-system')
# Keep the boot-time IP repair compatible with the added public aliases.
repair=pathlib.Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/repair-local-network.py')
text=repair.read_text()
text=text.replace("if name=='commons-services-pm-staff-portal-api': spec['hosts']=['partner-management-api.openg2p.localhost']", "if name=='commons-services-pm-staff-portal-api': spec['hosts']=list(dict.fromkeys(spec['hosts']+['partner-management-api.openg2p.localhost']))")
text=text.replace("if name=='bridge-bene-portal-api': spec['hosts']=['bridge-beneficiary-api.openg2p.localhost']", "if name=='bridge-bene-portal-api': spec['hosts']=list(dict.fromkeys(spec['hosts']+['bridge-beneficiary-api.openg2p.localhost']))")
text=text.replace("hostnames={'openg2p.localhost'}","hostnames={'openg2p.localhost','nigeriag2p.com'}")
text=text.replace("if 'openg2p.localhost' not in line and 'openg2p-ux.localhost' not in line", "if 'openg2p.localhost' not in line and 'openg2p-ux.localhost' not in line and 'nigeriag2p.com' not in line")
repair.write_text(text)
# Shared certificate is used only internally; the tunnel connects over loopback HTTP.
existing=pathlib.Path('/etc/nginx/sites-available/openg2p-lab').read_text()
existing=existing.replace('server_name *.openg2p.localhost beneficiary.openg2p-ux.localhost;', 'server_name *.openg2p.localhost beneficiary.openg2p-ux.localhost *.nigeriag2p.com;')
existing=existing.replace('server_name openg2p.localhost;', 'server_name openg2p.localhost nigeriag2p.com;')
pathlib.Path('/etc/nginx/sites-available/openg2p-lab').write_text(existing)
public=ROOT/'public-home'; public.mkdir(exist_ok=True)
html=convert((ROOT/'home/index.html').read_text())
html=re.sub(r'<a class="card" href="https://minio[^>]+>.*?</a>','',html,flags=re.S)
html=re.sub(r'<footer>.*?</footer>','<footer><p class="small">IQS Nigeria demonstration sandbox. All people, identities and payments are synthetic. Sign in using the application credentials supplied by the project team.</p><p class="small"><a href="https://portal-admin.nigeriag2p.com/web">Beneficiary programme admin</a></p></footer>',html,flags=re.S)
html=html.replace('LOCAL DEVELOPMENT ENVIRONMENT','NIGERIA DEMONSTRATION SANDBOX').replace('local synthetic identity login','synthetic identity login')
(public/'index.html').write_text(html)
allowed=['pbms','register','registry','staff-portal','beneficiary','awe','master-data-ui','master-data','partner-management','partner-management-api','consent-manager','staff-iam','iam-staff-ui','odk','superset','portal-admin','staff-register','pbms-api','keycloak']
config='''# Only cloudflared can reach this loopback-only public origin.
server {
 listen 127.0.0.1:18080 default_server;
 server_name _;
 return 404;
}
server {
 listen 127.0.0.1:18080;
 server_name nigeriag2p.com www.nigeriag2p.com;
 root /opt/openg2p-lab/public-home;
 include /etc/nginx/snippets/iqs-brand.conf;
 location / { try_files $uri $uri/ =404; }
}
server {
 listen 127.0.0.1:18080;
 server_name '''+' '.join(h+'.'+DOMAIN for h in allowed)+''';
 client_max_body_size 100m;
 large_client_header_buffers 4 32k;
 include /etc/nginx/snippets/iqs-brand.conf;
 # Identity administration remains available through local access only.
 location ~ ^/(admin|realms/master)(/|$) { if ($host = keycloak.nigeriag2p.com) { return 404; } proxy_pass http://127.0.0.1:30080; proxy_set_header Host $host; }
 # Odoo's database manager is not part of the public sandbox.
 location ^~ /web/database/ { return 404; }
 location / {
  proxy_pass http://127.0.0.1:30080;
  proxy_http_version 1.1;
  proxy_set_header Host $host;
  proxy_set_header Accept-Encoding "";
  proxy_set_header X-Forwarded-Proto https;
  proxy_set_header X-Forwarded-Host $host;
  proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
  proxy_set_header Upgrade $http_upgrade;
  proxy_set_header Connection "upgrade";
  proxy_buffer_size 32k;
  proxy_buffers 8 32k;
  proxy_read_timeout 300s;
 }
}
'''
pathlib.Path('/etc/nginx/sites-available/iqs-public').write_text(config)
link=pathlib.Path('/etc/nginx/sites-enabled/iqs-public')
if not link.exists():link.symlink_to('/etc/nginx/sites-available/iqs-public')
run(['nginx','-t']);run(['systemctl','reload','nginx'])
(ROOT/'public-hostnames.json').write_text(json.dumps([DOMAIN,'www.'+DOMAIN]+[h+'.'+DOMAIN for h in allowed],indent=2))
print('Public origin prepared on loopback port 18080; no public DNS routes have been published.')
