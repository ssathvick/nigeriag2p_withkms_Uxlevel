import subprocess,re,json
def run(*args):return subprocess.check_output(args,text=True,stderr=subprocess.DEVNULL)
s=run('kubectl','logs','-n','nigeria','deployment/commons-services-iam-staff-portal-api','--tail=120')
s=re.sub(r'eyJ[A-Za-z0-9_.-]+','[REDACTED_TOKEN]',s)
s=re.sub(r'(code|state|session_state|client_secret|password|access_token|refresh_token)=([^ &"\s]+)',r'\1=[REDACTED]',s)
print(s[-16000:])
d=json.loads(run('kubectl','get','deployment','-n','nigeria','commons-services-iam-staff-portal-api','-o','json'))
for c in d['spec']['template']['spec']['containers']:
 print(c['name'],c['image']);print('Env names:',[v['name'] for v in c.get('env',[])])
