import sys,subprocess,xml.etree.ElementTree as ET
sys.path.insert(0,'/mnt/h/Nigeria_Mosip/codex/openg2p-lab')
from labdb import query
q='''select s.token from sessions s join actors a on a.id=s."actorId" join field_keys f on f."actorId"=a.id where a."displayName"='OnePlus sample-only upload' and a."deletedAt" is null and f."projectId"=1 order by s."createdAt" desc limit 1;'''
expected='https://odk.nigeriag2p.com/v1/key/'+query('odkdb',q).strip()+'/projects/1'
adb='/mnt/h/Nigeria_Mosip/codex/openg2p-lab/field-app/android/tools/platform-tools/adb.exe'; b=[adb,'-P','5038','-s','6b8f8c38']
subprocess.run(b+['shell','uiautomator','dump','/sdcard/field-secret.xml'],capture_output=True,check=True)
try:
 raw=subprocess.check_output(b+['shell','cat','/sdcard/field-secret.xml']); node=ET.fromstring(raw).find('.//node[@class="android.widget.EditText"]'); print('Test project credential entered correctly:',bool(node is not None and node.get('text')==expected))
finally:subprocess.run(b+['shell','rm','-f','/sdcard/field-secret.xml'],capture_output=True)
