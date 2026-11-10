import sys,json,subprocess
sys.path.insert(0,'/opt/openg2p-lab/registration')
import registration_app as r
import jos_connected as j
for key in j.IDS:
 x=j.run(r,key);l,details=j.calculation(r,x);print(key,l)
logs=subprocess.check_output(['kubectl','-n','nigeria','logs','deploy/pbms-celery-worker','--tail=100'],text=True)
print('\n'.join(line for line in logs.splitlines() if any(x in line.lower() for x in ['error','envelope','exception','traceback'])))
