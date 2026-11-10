import subprocess,re,sys
from pathlib import Path
sys.path.insert(0,'/opt/openg2p-lab/registration')
import registration_app as r
log=subprocess.check_output(['kubectl','-n','nigeria','logs','deploy/openg2p-g2p-bridge-example-bank-api','--tail=120'],text=True,stderr=subprocess.DEVNULL)
private=r.ROOT/'phase1-private-tests';private.mkdir(exist_ok=True,mode=0o700);p=private/'statement-api.log';p.write_text(log);p.chmod(0o600)
matches=re.findall(r'[a-zA-Z_.]+(?:Error|Exception):[^\n]+',log.replace('\\n','\n'))
for line in matches[-4:]:print(re.sub(r'postgres(?:ql)?[^ ]*','[database URI]',line)[:300])
