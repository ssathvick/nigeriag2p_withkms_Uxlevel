import subprocess,pathlib,json
root=pathlib.Path('/opt/openg2p-lab')
checks=[]
hosts={
 'pbms.openg2p.localhost':'/web/login',
 'registry.openg2p.localhost':'/web/login',
 'portal-admin.openg2p.localhost':'/web/login',
 'register.openg2p.localhost':'/en',
 'beneficiary.openg2p-ux.localhost':'/selfservice/en/home',
 'staff-portal.openg2p.localhost':'/en',
 'awe.openg2p.localhost':'/',
 'master-data-ui.openg2p.localhost':'/en',
 'partner-management.openg2p.localhost':'/',
 'consent-manager.openg2p.localhost':'/',
 'openg2p.localhost':'/',
 'keycloak.openg2p.localhost':'/realms/staff/protocol/openid-connect/auth?client_id=staff-portal&redirect_uri=https%3A%2F%2Fstaff-portal.openg2p.localhost%2Fapi%2Fauth%2Fcallback%2Fkeycloak&response_type=code&scope=openid&prompt=login'
}
for host,path in hosts.items():
 p=subprocess.run(['curl','-sS','--cacert',str(root/'tls/ca.crt'),'--resolve',host+':443:127.0.0.1','https://'+host+path],capture_output=True,text=True,check=True)
 passed='/iqs-brand/iqs-brand.js' in p.stdout and '/iqs-brand/iqs-brand.css' in p.stdout
 checks.append({'host':host,'theme_injected':passed})
 print(host,'IQS theme present' if passed else 'FAILED')
for asset in ['iqs-brand.js','iqs-brand.css','iqs-logo.png']:
 p=subprocess.run(['curl','-sS','--fail','--cacert',str(root/'tls/ca.crt'),'--resolve','pbms.openg2p.localhost:443:127.0.0.1','https://pbms.openg2p.localhost/iqs-brand/'+asset],capture_output=True,check=True)
 assert p.stdout==(root/'branding'/asset).read_bytes(),asset+' content mismatch'
 checks.append({'asset':asset,'content_verified':True})
assert all(c.get('theme_injected',True) for c in checks)
pathlib.Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/branding/verification.json').write_text(json.dumps(checks,indent=2))
print('12 UI responses and 3 branding assets verified with TLS certificate validation.')
