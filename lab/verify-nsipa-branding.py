"""Read-only deployment checks for the public NSIPA presentation assets."""
from pathlib import Path
import concurrent.futures, requests, json, hashlib, subprocess
root=Path('/opt/openg2p-lab')
source=Path(__file__).resolve().parent
hosts=['g2p.wverve.in','g2p-pbms.wverve.in','g2p-register.wverve.in','g2p-registry.wverve.in','g2p-staff-portal.wverve.in','g2p-beneficiary.wverve.in','g2p-awe.wverve.in','g2p-master-data-ui.wverve.in','g2p-partner-management.wverve.in','g2p-consent-manager.wverve.in','g2p-iam-staff-ui.wverve.in','g2p-odk.wverve.in','g2p-superset.wverve.in','g2p-portal-admin.wverve.in','g2p-keycloak.wverve.in']
def check(host):
    # Test the actual public virtual host on its loopback origin without changing TLS configuration.
    session=requests.Session();headers={'Host':host}
    checks={}
    for asset in ['iqs-brand.js','iqs-brand.css','nsipa-logo.svg','nsipa-wordmark.svg','nsipa-symbol.svg']:
        r=session.get('http://127.0.0.1:18080/iqs-brand/'+asset,headers=headers,timeout=20)
        checks[asset]=r.status_code==200 and r.content==(root/'branding'/asset).read_bytes()
    for path in ['/resources/02qxz/login/staff-portal/img/keycloak.svg','/openg2p-logo-dark.svg','/static/assets/images/superset-logo-horiz.png','/favicon.ico']:
        r=session.get('http://127.0.0.1:18080'+path,headers=headers,timeout=20)
        expected='nsipa-symbol.svg' if path.endswith('.ico') else 'nsipa-wordmark.svg'
        checks[path]=r.status_code==200 and r.content==(root/'branding'/expected).read_bytes() and 'image/svg+xml' in r.headers.get('Content-Type','')
    return {'host':host,'checks':checks,'passed':all(checks.values())}
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool: results=list(pool.map(check,hosts))
for result in results: print(result['host'], 'PASS' if result['passed'] else 'FAIL',len(result['checks']),'asset checks')
data=json.loads(subprocess.check_output(['kubectl','-n','nigeria','get','deployments,statefulsets','-o','json']))['items']
not_ready=[i['metadata']['name'] for i in data if i.get('status',{}).get('readyReplicas',0)<i['spec'].get('replicas',1)]
report={'hosts':results,'workloads':len(data),'not_ready':not_ready}
(source/'branding/nsipa-verification.json').write_text(json.dumps(report,indent=2))
assert all(r['passed'] for r in results)
assert not not_ready,not_ready
print(len(results)*9,'asset checks passed;',len(data),'workloads ready.')
