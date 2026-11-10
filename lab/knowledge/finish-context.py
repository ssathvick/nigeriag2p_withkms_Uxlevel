from pathlib import Path
import shutil,datetime,subprocess
src=Path(__file__).resolve().parents[1];app=Path('/opt/openg2p-lab/registration');backup=Path('/opt/openg2p-lab/knowledge-corrections')/('followup-'+datetime.datetime.now().strftime('%Y%m%d%H%M%S'));backup.mkdir(mode=0o700)
tags='<link rel="stylesheet" href="/iqs-brand/knowledge-help.css?v=nsipa-20261110"><script defer src="/iqs-brand/knowledge-context.js?v=nsipa-20261110"></script><script defer src="/iqs-brand/knowledge-help.js?v=nsipa-20261110"></script>'
for i,p in enumerate([src/'registration-ui/base.html',app/'templates/base.html']):
 s=p.read_text();shutil.copy2(p,backup/('base-'+str(i)))
 if '/knowledge-help.js' not in s:p.write_text(s.replace('</head>',tags+'</head>'))
for i,p in enumerate([src/'local_ai.py',app/'local_ai.py']):
 s=p.read_text();shutil.copy2(p,backup/('local-ai-'+str(i)))
 s=s.replace('NigeriaG2P','NSIPA').replace("result=json.loads(response.json()['message']['content'])", "payload=response.json()\n  if payload.get('done_reason')=='length':abort(503,'The generated guidance was incomplete. Try a shorter question or read the linked published guidance.')\n  result=json.loads(payload['message']['content'])")
 # Remove whole low-ranked sources instead of cutting a sentence or JSON object.
 s=s.replace("source_text=json.dumps(sources,ensure_ascii=False)[:23000]", "while len(json.dumps(sources,ensure_ascii=False))>23000 and len(sources)>1:sources.pop()\n  source_text=json.dumps(sources,ensure_ascii=False)\n  if len(source_text)>23000:abort(503,'This guidance is too long for a generated answer. Read the published article directly.')")
 s=s.replace("},ensure_ascii=False)[:24000]", "},ensure_ascii=False)")
 p.write_text(s)
subprocess.run(['/opt/openg2p-lab/registration-venv/bin/python','-m','py_compile',str(app/'local_ai.py')],check=True)
subprocess.run(['systemctl','restart','iqs-registration.service'],check=True)
print('Updated registration help loader and protected AI answers from token-limit truncation. Backup: '+str(backup))
