import json,sys,subprocess,re
from pathlib import Path
import requests
sys.path.insert(0,'/mnt/h/Nigeria_Mosip/codex/openg2p-lab');from labdb import query
w=Path(__file__).parent;r=Path('/opt/openg2p-lab/phone-fault-test')
(w/'fault-events.jsonl').write_bytes((r/'events.jsonl').read_bytes())
token=query('odkdb', '''select s.token from sessions s join actors a on a.id=s."actorId" where a."displayName"='OnePlus sample-only upload' and a."deletedAt" is null order by s."createdAt" desc limit 1;''').strip()
out=[]
for host in ['odk.nigeriag2p.com','g2p-odk.wverve.in']:
 resp=requests.post('https://'+host+'/v1/key/'+token+'/projects/1/submission',headers={'X-OpenRosa-Version':'1.0'},files={'xml_submission_file':('submission.xml',(w/'fault-submission.xml').read_bytes(),'text/xml')},verify='/opt/openg2p-lab/registration/ca-bundle.crt',timeout=30)
 out.append({'host':host,'status':resp.status_code});assert resp.status_code==201
(w/'fault-openrosa-replays.json').write_text(json.dumps(out,indent=2))
for name in ['/etc/nginx/conf.d/iqs-dual-domain.conf','/etc/nginx/sites-enabled/iqs-wverve']:
 p=Path(name);s=p.read_text();lines=s.splitlines(True);removed=[x for x in lines if 'location ^~ /__nsipa_fault_' in x];assert len(removed)==1;p.write_text(''.join(x for x in lines if x not in removed))
subprocess.run(['nginx','-t'],check=True,capture_output=True);subprocess.run(['systemctl','reload','nginx'],check=True);subprocess.run(['systemctl','stop','nsipa-phone-fault'],check=True)
print('Two OpenRosa identical-instance replays returned 201; isolated routes removed and relay stopped')
