import pathlib,json,base64,requests,yaml,subprocess,datetime
P=pathlib.Path('/mnt/h/Nigeria_Mosip/NSIPA-Private-Access-20261111'); B=P/'console-route-backup';B.mkdir(exist_ok=True)
c=json.loads(base64.b64decode(''.join(pathlib.Path('/root/.cloudflared/cert.pem').read_text().splitlines()[1:-1])))
s=requests.Session();s.headers['Authorization']='Bearer '+c['apiToken'];api='https://api.cloudflare.com/client/v4'
r=s.get(api+'/zones',params={'per_page':50},timeout=30);r.raise_for_status();zones={z['name']:z['id'] for z in r.json()['result']};print('Accessible zones:',list(zones))
config=pathlib.Path('/etc/cloudflared/config.yml');d=yaml.safe_load(config.read_text());target=d['tunnel']+'.cfargotunnel.com'
hosts=['minio.nigeriag2p.com','kafka.nigeriag2p.com','g2p-minio.wverve.in','g2p-kafka.wverve.in']
assert 'nigeriag2p.com' in zones
f=pathlib.Path('/etc/nginx/conf.d/nsipa-console-access.conf')
for path in [config,f]:
 if path.exists() and not (B/path.name).exists():(B/path.name).write_bytes(path.read_bytes())
tls='listen 443 ssl; ssl_certificate /opt/openg2p-lab/tls/server.crt; ssl_certificate_key /opt/openg2p-lab/tls/server.key;'
# Canonical Kafka forwards to its configured OAuth hostname; preserve paths.
text='server { listen 127.0.0.1:18084; '+tls+' server_name kafka.nigeriag2p.com; return 302 https://g2p-kafka.wverve.in$request_uri; }\n'
text+='server { listen 127.0.0.1:18084; server_name g2p-kafka.wverve.in; location / { proxy_pass http://127.0.0.1:30080; proxy_set_header Host g2p-kafka.wverve.in; proxy_set_header X-Forwarded-Proto https; proxy_set_header X-Forwarded-Host g2p-kafka.wverve.in; proxy_http_version 1.1; proxy_buffer_size 32k; proxy_buffers 8 32k; } }\n'
svc=json.loads(subprocess.check_output(['kubectl','-n','nigeria','get','svc/commons-minio','-o','json']))
text+='server { listen 127.0.0.1:18084; '+tls+' server_name minio.nigeriag2p.com; location / { proxy_pass http://'+svc['spec']['clusterIP']+':9001; proxy_set_header Host $host; proxy_set_header X-Forwarded-Proto https; proxy_http_version 1.1; proxy_set_header Upgrade $http_upgrade; proxy_set_header Connection "upgrade"; } }\n'
text+='server { listen 127.0.0.1:18084; server_name g2p-minio.wverve.in; location / { proxy_pass http://'+svc['spec']['clusterIP']+':9001; proxy_set_header Host $host; proxy_set_header X-Forwarded-Proto https; proxy_http_version 1.1; proxy_set_header Upgrade $http_upgrade; proxy_set_header Connection "upgrade"; } }\n'
f.write_text(text);subprocess.run(['nginx','-t'],check=True);subprocess.run(['systemctl','reload','nginx'],check=True)
for h in hosts:
 if not any(x.get('hostname')==h for x in d['ingress']):d['ingress'].insert(-1,{'hostname':h,'service':'http://127.0.0.1:18084'})
config.write_text(yaml.safe_dump(d,sort_keys=False));subprocess.run(['cloudflared','tunnel','ingress','validate'],check=True);subprocess.run(['systemctl','restart','cloudflared'],check=True)
for h in hosts:
 zone='nigeriag2p.com' if h.endswith('.nigeriag2p.com') else 'wverve.in'
 if zone not in zones:print('DNS pending administrator:',h);continue
 url=api+'/zones/'+zones[zone]+'/dns_records'
 r=s.get(url,params={'name':h},timeout=30);r.raise_for_status();existing=r.json()['result']
 if existing:
  assert len(existing)==1 and existing[0]['type']=='CNAME' and existing[0]['content']==target,'Conflicting DNS record: '+h
 else:
  r=s.post(url,json={'type':'CNAME','name':h,'content':target,'proxied':True,'ttl':1},timeout=30);r.raise_for_status();assert r.json()['success']
 print('DNS configured:',h)
(P/'Console-Route-Change.json').write_text(json.dumps({'hosts':hosts,'kafka_canonical':'302 to existing alternate OAuth hostname','backup':str(B),'date':datetime.datetime.now().isoformat()},indent=2))
