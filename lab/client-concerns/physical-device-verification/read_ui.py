import subprocess,xml.etree.ElementTree as ET,json,re
from pathlib import Path
ADB=str(Path('openg2p-lab/field-app/android/tools/platform-tools/adb.exe').resolve());BASE=[ADB,'-s','6b8f8c38']
def run(*args):return subprocess.run(BASE+list(args),capture_output=True,check=True,timeout=30).stdout
run('shell','uiautomator','dump','/sdcard/nsipa-test-ui.xml')
try:
 root=ET.fromstring(run('shell','cat','/sdcard/nsipa-test-ui.xml'));nodes=[]
 for n in root.iter('node'):
  if n.get('package')!='org.nigeriag2p.field':continue
  value=n.get('text','')
  if '/v1/key/' in value:value='[private connection URL]'
  if value:nodes.append({'text':value,'class':n.get('class'),'bounds':n.get('bounds')})
 print(json.dumps(nodes))
finally:run('shell','rm','-f','/sdcard/nsipa-test-ui.xml')
