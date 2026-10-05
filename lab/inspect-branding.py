import subprocess,json
hosts=['pbms','register','staff-portal','keycloak','awe','master-data-ui','partner-management','consent-manager']
for host in hosts:
 url='https://'+host+'.openg2p.localhost'+('/web/login' if host=='pbms' else '/')
 p=subprocess.run(['curl','-sS','-I','--resolve',host+'.openg2p.localhost:443:127.0.0.1',url],capture_output=True,text=True)
 print(host,p.stdout[:1800],p.stderr[:120])
