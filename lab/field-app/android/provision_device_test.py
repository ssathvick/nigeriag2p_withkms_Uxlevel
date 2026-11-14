import sys,subprocess,shlex
sys.path.insert(0,'/mnt/h/Nigeria_Mosip/codex/openg2p-lab')
from labdb import query
sql='''select s.token from sessions s join actors a on a.id=s."actorId" join field_keys f on f."actorId"=a.id where a."displayName"='OnePlus sample-only upload' and a."deletedAt" is null and f."projectId"=1 order by s."createdAt" desc limit 1;'''
token=query('odkdb',sql).strip(); assert token and '\n' not in token
url='https://odk.nigeriag2p.com/v1/key/'+token+'/projects/1'
adb='/mnt/h/Nigeria_Mosip/codex/openg2p-lab/field-app/android/tools/platform-tools/adb.exe'
base=[adb,'-P','5038','-s','6b8f8c38']
def run(*args):
 p=subprocess.run(base+list(args),capture_output=True,text=True,timeout=30)
 if p.returncode:raise RuntimeError('ADB input failed')
run('shell','input','tap','300','985')
run('shell','input','text',shlex.quote(url))
run('shell','input','keyevent','4')
print('Test project URL entered on the device (credential omitted).')
