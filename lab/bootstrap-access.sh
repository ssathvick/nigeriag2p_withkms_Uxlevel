#!/usr/bin/env bash
set -euo pipefail
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml
LAB=/opt/openg2p-lab
mkdir -p "$LAB/tls"
if [ ! -f "$LAB/tls/ca.key" ]; then
  openssl req -x509 -newkey rsa:3072 -nodes -keyout "$LAB/tls/ca.key" -out "$LAB/tls/ca.crt" -days 3650 -subj '/CN=Nigeria OpenG2P Local Lab CA' -addext 'basicConstraints=critical,CA:TRUE' -addext 'keyUsage=critical,keyCertSign,cRLSign' 2>/dev/null
  openssl req -new -newkey rsa:2048 -nodes -keyout "$LAB/tls/server.key" -out "$LAB/tls/server.csr" -subj '/CN=openg2p.localhost' 2>/dev/null
  printf 'subjectAltName=DNS:openg2p.localhost,DNS:*.openg2p.localhost\nextendedKeyUsage=serverAuth\n' > "$LAB/tls/extensions"
  openssl x509 -req -in "$LAB/tls/server.csr" -CA "$LAB/tls/ca.crt" -CAkey "$LAB/tls/ca.key" -CAcreateserial -out "$LAB/tls/server.crt" -days 825 -extfile "$LAB/tls/extensions" 2>/dev/null
  chmod 600 "$LAB/tls/"*.key
fi
cp "$LAB/tls/ca.crt" /usr/local/share/ca-certificates/openg2p-lab.crt
update-ca-certificates > /tmp/openg2p-ca.log
cp "$LAB/tls/ca.crt" /mnt/h/Nigeria_Mosip/codex/openg2p-lab/openg2p-lab-ca.crt
cat > /etc/nginx/sites-available/openg2p-lab <<'NGINX'
server {
    listen 443 ssl;
    server_name openg2p.localhost *.openg2p.localhost;
    ssl_certificate /opt/openg2p-lab/tls/server.crt;
    ssl_certificate_key /opt/openg2p-lab/tls/server.key;
    client_max_body_size 100m;
    large_client_header_buffers 4 32k;
    location / {
        proxy_pass http://127.0.0.1:30080;
        proxy_http_version 1.1;
        proxy_buffer_size 32k;
        proxy_buffers 8 32k;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto https;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Host $host;
        proxy_read_timeout 300s;
    }
}
NGINX
ln -sfn /etc/nginx/sites-available/openg2p-lab /etc/nginx/sites-enabled/openg2p-lab
nginx -t
systemctl restart nginx
kubectl apply -f - <<'YAML'
apiVersion: networking.istio.io/v1
kind: Gateway
metadata:
  name: internal
  namespace: nigeria
spec:
  selector:
    istio: ingressgateway
  servers:
    - port:
        number: 80
        name: http
        protocol: HTTP
      hosts:
        - '*.openg2p.localhost'
        - 'openg2p.localhost'
YAML
