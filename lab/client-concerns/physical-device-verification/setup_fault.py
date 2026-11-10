import pathlib,json,secrets,subprocess
r=pathlib.Path('/opt/openg2p-lab/phone-fault-test');r.mkdir(mode=0o700,exist_ok=True)
prefix='/__nsipa_fault_'+secrets.token_hex(16)
(r/'private.json').write_text(json.dumps({'prefix':prefix}));(r/'private.json').chmod(0o600)
(r/'control.json').write_text(json.dumps({'mode':'mid','domain':'odk.nigeriag2p.com'}))
route='\n location ^~ '+prefix+'/ { access_log off; proxy_pass http://127.0.0.1:18891; proxy_request_buffering off; proxy_buffering off; proxy_next_upstream off; proxy_read_timeout 25s; }\n'
targets=[('/etc/nginx/conf.d/iqs-dual-domain.conf',' server_name nigeriag2p.com'),('/etc/nginx/sites-enabled/iqs-wverve',' server_name g2p-minio-api.wverve.in')]
for i,(name,marker) in enumerate(targets):
 p=pathlib.Path(name);s=p.read_text();(r/('nginx-'+str(i)+'.bak')).write_text(s)
 pos=s.index('\n',s.index(marker))+1;p.write_text(s[:pos]+route+s[pos:])
subprocess.run(['nginx','-t'],check=True,capture_output=True)
subprocess.run(['systemctl','reload','nginx'],check=True)
print('Isolated test routes installed; private path omitted')
