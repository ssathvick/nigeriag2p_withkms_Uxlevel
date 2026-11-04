"""Deploy only dashboard presentation and routing, retaining a private rollback manifest."""
from pathlib import Path
import datetime,json,shutil,subprocess,time,re,hashlib
import requests
src=Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab')
root=Path('/opt/openg2p-lab/registration')
branding=Path('/opt/openg2p-lab/branding')
snippet=Path('/etc/nginx/snippets/iqs-brand.conf')
backup=root/'dashboard-backups'/datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
backup.mkdir(parents=True,mode=0o700)
targets=[(src/n,root/n) for n in ['platform_analytics.py','registration_app.py','analytics_sources.py','service_reporting.py']]
targets.append((src/'registration-ui/dashboard.html',root/'templates/dashboard.html'))
targets += [(src/'persona-ui/dist'/n,root/'static'/n) for n in ['dashboard.js','dashboard.css']]
targets += [(src/'persona-ui/dist'/n,branding/n) for n in ['site.js','site-shell.js','dashboard-landing.js','service-insights.js','service-insights.css']]
manifest=[]
homes=[Path('/opt/openg2p-lab')/folder/'index.html' for folder in ['home','public-home']]
for i,target in enumerate([t for _,t in targets]+[snippet]+homes):
 saved=backup/str(i)
 if target.exists():shutil.copy2(target,saved)
 manifest.append({'target':str(target),'saved':str(saved) if saved.exists() else None})
(backup/'manifest.json').write_text(json.dumps(manifest,indent=2))
try:
 for source,target in targets:shutil.copy2(source,target)
 for home in homes:
  version=hashlib.sha256((branding/'site.js').read_bytes()).hexdigest()[:12]
  home.write_text(re.sub(r'/iqs-brand/site\.js(?:\?v=[^"\s]*)?', '/iqs-brand/site.js?v='+version,home.read_text()))
 template=root/'templates/dashboard.html'
 version=hashlib.sha256((root/'static/dashboard.js').read_bytes()+(root/'static/dashboard.css').read_bytes()).hexdigest()[:12]
 template.write_text(template.read_text().replace('?v=20261104','?v='+version))
 s=snippet.read_text()
 injection='<link rel="stylesheet" href="/iqs-brand/service-insights.css?v=20261104"><script defer src="/iqs-brand/service-insights.js?v=20261104"></script>'
 s=s.replace("sub_filter '"+injection+"</head>'", "sub_filter '</head>'")
 if '/service-insights.js' not in s:
  s=s.replace("</head>';",injection+"</head>';")
 if '/dashboard-landing.js' not in s:
  s=s.replace("</head>';", "<script src=\"/iqs-brand/dashboard-landing.js\"></script></head>';")
 for name in ['dashboard-landing.js','site-shell.js','service-insights.js','service-insights.css']:
  version=hashlib.sha256((branding/name).read_bytes()).hexdigest()[:12]
  s=re.sub(r'/iqs-brand/'+re.escape(name)+r'(?:\?v=[^"\s]*)?', '/iqs-brand/'+name+'?v='+version,s)
 assert "sub_filter '</head>'" in s
 snippet.write_text(s)
 subprocess.run(['/opt/openg2p-lab/registration-venv/bin/python','-m','py_compile',str(root/'platform_analytics.py'),str(root/'registration_app.py')],check=True)
 subprocess.run(['nginx','-t'],check=True)
 subprocess.run(['systemctl','restart','iqs-registration.service'],check=True)
 for _ in range(30):
  try:
   if requests.get('http://127.0.0.1:18081/registration/health',timeout=2).status_code==200:break
  except requests.RequestException:pass
  time.sleep(.3)
 else:raise RuntimeError('Registration health check failed')
 subprocess.run(['systemctl','reload','nginx'],check=True)
 for n in ['dashboard.js','dashboard.css']:
  assert requests.get('http://127.0.0.1:18081/registration/static/'+n,timeout=5).status_code==200
 assert requests.get('http://127.0.0.1:18081/registration/api/analytics',timeout=5).status_code==401
 print('Dashboards installed; anonymous reporting denied. Rollback manifest:',backup/'manifest.json')
except Exception:
 for entry in manifest:
  target=Path(entry['target'])
  if entry['saved']:shutil.copy2(entry['saved'],target)
  elif target.exists():target.unlink()
 subprocess.run(['systemctl','restart','iqs-registration.service'])
 subprocess.run(['nginx','-t'],check=True)
 subprocess.run(['systemctl','reload','nginx'])
 raise
