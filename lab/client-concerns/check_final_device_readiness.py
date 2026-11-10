import requests,hashlib,json,datetime,subprocess
from pathlib import Path
work=Path(__file__).parent/'final-e2e-verification';results=[]
for host in ['nigeriag2p.com','g2p.wverve.in']:
 url='https://'+host+'/field-preview/android/nsipa-household-intake-v0.7.apk'
 r=requests.get(url,verify='/opt/openg2p-lab/registration/ca-bundle.crt',timeout=40);r.raise_for_status();digest=hashlib.sha256(r.content).hexdigest()
 assert digest=='a79998731cf9bb8aa51d0a2d7d7712b73523e3ef924ed116d153c95021308bfb'
 results.append({'url':url,'status':r.status_code,'bytes':len(r.content),'sha256':digest})
out={'checked_at_ist':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=5,minutes=30))).isoformat(),'apk_checks':results,'physical_run':'Not performed; no connected device in adb inventory.'}
(work/'device-readiness.json').write_text(json.dumps(out,indent=2));print('PASS both APK downloads available and identical to verified v0.7 build; no physical-device result claimed')
