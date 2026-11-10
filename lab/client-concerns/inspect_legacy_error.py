import subprocess,json
r=subprocess.run(['kubectl','-n','nigeria','logs','deployment/register-staff-portal-api','--since=8m'],capture_output=True,text=True)
seen=set()
for line in r.stdout.splitlines():
 try:d=json.loads(line)
 except:continue
 if d.get('level') in ['ERROR','WARNING']:
  msg=d.get('msg',str(d))
  if msg not in seen:print(msg[:1800]);seen.add(msg)
