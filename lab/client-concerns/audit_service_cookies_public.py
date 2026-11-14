import audit_service_cookies as a
import socket,json,concurrent.futures,datetime
m=json.loads((a.OUT.parent/'dual-domain/hostname-map.json').read_text())
r=a.requests.get('https://cloudflare-dns.com/dns-query',params={'name':'g2p.wverve.in','type':'A'},headers={'accept':'application/dns-json'},timeout=20);r.raise_for_status()
ip=next(x['data'] for x in r.json()['Answer'] if x['type']==1)
original=socket.getaddrinfo
socket.getaddrinfo=lambda host,port,*args,**kw:original(ip if host in m.values() else host,port,*args,**kw)
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:rows=list(pool.map(a.audit,a.SERVICES))
(a.OUT/'service-cookie-audit-public.json').write_text(json.dumps({'checked_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'mode':'public-edge','services':rows},indent=2))
print(json.dumps([{'service':x['service'],'status':x['status'],'error':x.get('error'),'invalid_cookie_domains':x['invalid_cookie_domains']} for x in rows],indent=2))
