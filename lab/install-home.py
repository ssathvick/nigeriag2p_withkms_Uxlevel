import pathlib,subprocess
path=pathlib.Path('/etc/nginx/sites-available/openg2p-lab')
config=path.read_text()
if 'proxy_buffer_size' not in config:
 config=config.replace('proxy_http_version 1.1;','proxy_http_version 1.1;\n        proxy_buffer_size 32k;\n        proxy_buffers 8 32k;')
config=config.replace('        large_client_header_buffers 4 32k;\n','')
if 'large_client_header_buffers' not in config:
 config=config.replace('client_max_body_size 100m;','client_max_body_size 100m;\n    large_client_header_buffers 4 32k;')
if 'server_name openg2p.localhost;' not in config:
 config+='''\nserver {
 listen 443 ssl;
 server_name openg2p.localhost;
 ssl_certificate /opt/openg2p-lab/tls/server.crt;
 ssl_certificate_key /opt/openg2p-lab/tls/server.key;
 root /opt/openg2p-lab/home;
 index index.html;
 location / { try_files $uri $uri/ =404; }
}\n'''
 config=config.replace('server_name openg2p.localhost *.openg2p.localhost;','server_name *.openg2p.localhost;')
path.write_text(config)
subprocess.run(['nginx','-t'],check=True)
subprocess.run(['systemctl','reload','nginx'],check=True)
