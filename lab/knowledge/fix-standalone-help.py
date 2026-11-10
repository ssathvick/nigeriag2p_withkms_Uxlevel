from pathlib import Path
import datetime,shutil,subprocess,json
src=Path(__file__).resolve().parents[1];app=Path('/opt/openg2p-lab/registration');backup=Path('/opt/openg2p-lab/knowledge-corrections')/('standalone-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));backup.mkdir(mode=0o700)
tags='<link rel="stylesheet" href="/iqs-brand/knowledge-help.css?v=auth-restored-20261110"><script defer src="/iqs-brand/knowledge-context.js?v=auth-restored-20261110"></script><script defer src="/iqs-brand/knowledge-help.js?v=auth-restored-20261110"></script>'
changed=[]
for folder in [src/'registration-ui',app/'templates']:
 for p in folder.glob('*.html'):
  s=p.read_text()
  if '</head>' not in s or '/knowledge-help.js' in s:continue
  shutil.copy2(p,backup/(folder.name+'-'+p.name));p.write_text(s.replace('</head>',tags+'</head>'));changed.append(str(p))
subprocess.run(['systemctl','restart','iqs-registration'],check=True);print(json.dumps({'updated':changed,'backup':str(backup)}))
