import subprocess,json
logs=subprocess.check_output(['kubectl','-n','nigeria','logs','deploy/register-staff-portal-api','--tail=250'],text=True,stderr=subprocess.DEVNULL)
for line in logs.splitlines():
 try:
  row=json.loads(line)
  if any(x in str(row.get('level','') or row.get('levelname','')).upper() for x in ['ERROR','CRITICAL']):print(json.dumps({k:str(v)[:2000] for k,v in row.items() if k in ['msg','message','exc_info','exception','traceback','type','level']}))
 except Exception:
  if 'Error' in line or 'Traceback' in line:print(line[:500])
