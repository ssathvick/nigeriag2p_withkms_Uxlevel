import sys,subprocess,shlex,xml.etree.ElementTree as ET,re,requests
sys.path.insert(0,'/mnt/h/Nigeria_Mosip/codex/openg2p-lab');from labdb import query
sql='''select s.token from sessions s join actors a on a.id=s."actorId" join field_keys f on f."actorId"=a.id where a."displayName"='OnePlus sample-only upload' and a."deletedAt" is null and f."projectId"=1 order by s."createdAt" desc limit 1;'''
token=query('odkdb',sql).strip();assert token and '\n' not in token
import json
from pathlib import Path
url='https://odk.nigeriag2p.com'+json.loads(Path('/opt/openg2p-lab/phone-fault-test/private.json').read_text())['prefix']
r=requests.get(url+'/formList',headers={'X-OpenRosa-Version':'1.0'},verify='/opt/openg2p-lab/registration/ca-bundle.crt',timeout=30);print('Connection check HTTP',r.status_code,'type',r.headers.get('Content-Type'));assert r.status_code==200 and 'nsipa_field_household_demo' in r.text
adb='/mnt/h/Nigeria_Mosip/codex/openg2p-lab/field-app/android/tools/platform-tools/adb.exe';base=[adb,'-s','6b8f8c38']
def run(*args):
 p=subprocess.run(base+list(args),capture_output=True,timeout=30)
 if p.returncode:raise RuntimeError('Device operation failed')
 return p.stdout
run('shell','uiautomator','dump','/sdcard/nsipa-connection-test.xml')
try:
 root=ET.fromstring(run('shell','cat','/sdcard/nsipa-connection-test.xml'));assert any(n.get('text')=='Connection settings' for n in root.iter('node'))
 node=root.find('.//node[@class="android.widget.EditText"]');coords=list(map(int,re.findall(r'\d+',node.get('bounds'))));run('shell','input','tap',str((coords[0]+coords[2])//2),str((coords[1]+coords[3])//2))
 run('shell','input','keycombination','113','29');run('shell','input','text',shlex.quote(url));run('shell','input','keyevent','4')
 run('shell','uiautomator','dump','/sdcard/nsipa-connection-test.xml');root=ET.fromstring(run('shell','cat','/sdcard/nsipa-connection-test.xml'));node=root.find('.//node[@class="android.widget.EditText"]');assert node.get('text')==url,'Private connection entry mismatch'
 button=next(n for n in root.iter('node') if n.get('text')=='Save connection');coords=list(map(int,re.findall(r'\d+',button.get('bounds'))));run('shell','input','tap',str((coords[0]+coords[2])//2),str((coords[1]+coords[3])//2))
 print('Dedicated sample connection validated and saved on phone; credentials omitted.')
finally:run('shell','rm','-f','/sdcard/nsipa-connection-test.xml')





