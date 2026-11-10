"""Prepare NSIPA help corrections without changing service identifiers or URLs."""
from pathlib import Path
import re,json
ROOT=Path(__file__).resolve().parents[1]
def edit(path,old,new):
 p=ROOT/path;s=p.read_text(encoding='utf-8');assert old in s,(path,old);p.write_text(s.replace(old,new),encoding='utf-8')
edit('knowledge/context.js',".split('.')[0]",".split('.')[0].replace(/^g2p-/, '')")
edit('knowledge/context.js','(enrollment|membership|cycle)','(enrollment|membership)')
edit('knowledge/help.js',"!location.hostname.endsWith('nigeriag2p.com')||location.hostname.startsWith('keycloak.')","!(/(^|\\.)nigeriag2p\\.com$/.test(location.hostname)||/^g2p(?:-[a-z0-9-]+)?\\.wverve\\.in$/.test(location.hostname)||location.hostname==='pbms.openg2p.localhost')||/^(keycloak\\.|g2p-keycloak\\.)/.test(location.hostname)")
edit('knowledge/help.js',"const root='https://nigeriag2p.com/registration'","const root=(location.hostname.endsWith('wverve.in')?'https://g2p.wverve.in':'https://nigeriag2p.com')+'/registration'")
edit('knowledge/help.js',"[role=\"dialog\"],.modal.show,.o_dialog","[role=\"dialog\"],[role=\"alertdialog\"],.modal.show,.o_dialog")
edit('knowledge/help.js',"].find(el=>el.id!=='ng-km-panel'&&visible(el))", "].filter(el=>el.id!=='ng-km-panel'&&visible(el)).at(-1)")
edit('knowledge/help.js',"area=modal.querySelector('[data-km-stage]')||modal.closest('[data-km-stage]')","area=modal.closest('[data-km-stage]')||modal.querySelector('[data-km-stage]')||screen")
# Prevent unrelated host application typography from clipping complete guidance.
p=ROOT/'knowledge/help.css'
p.write_text(p.read_text()+'''\n/* Guidance text must never inherit single-line cards or truncated table cells. */
#ng-km-panel p,#ng-km-panel li,#ng-km-panel h2,#ng-km-panel h3,#ng-km-panel h4,#ng-km-panel a,#ng-km-panel small,#ng-km-panel summary{white-space:normal!important;overflow:visible!important;text-overflow:clip!important;-webkit-line-clamp:unset!important;line-clamp:unset!important;max-height:none!important;height:auto!important;overflow-wrap:anywhere!important;word-break:normal!important}
#ng-km-panel p,#ng-km-panel h3,#ng-km-panel h4{display:block!important}
#ng-km-panel li{display:list-item!important}
#ng-km-panel .ng-km-content{flex:1 1 auto!important}
''')
edit('pbms-react/index.html','</head>','<link rel="stylesheet" href="/iqs-brand/knowledge-help.css?v=nsipa-20261110"><script defer src="/iqs-brand/knowledge-context.js?v=nsipa-20261110"></script><script defer src="/iqs-brand/knowledge-help.js?v=nsipa-20261110"></script></head>')
edit('deploy-pbms-react.py',' location = /pbms-ui {', ''' location = /iqs-brand/knowledge {
  proxy_pass http://127.0.0.1:18081/registration/api/knowledge;
  proxy_set_header Host g2p.wverve.in;
  proxy_set_header Cookie "";
  proxy_hide_header Set-Cookie;
 }
 location ^~ /iqs-brand/ {
  alias /opt/openg2p-lab/branding/;
  add_header Cache-Control "no-cache";
  add_header X-Content-Type-Options nosniff;
 }
 location = /pbms-ui {''')
edit('pbms-react/src/main.jsx','<main className="content">','<main className="content" data-km-screen="pbms" data-km-module="pbms" data-km-stage={item.label}>')
edit('pbms-react/src/main.jsx','<main className="login">','<main className="login" data-km-screen="pbms-login" data-km-module="pbms" data-km-stage="Sign in">')
edit('pbms-react/src/workflows.jsx','aria-label="Payment report"','aria-label="Payment report" data-km-module="pbms" data-km-stage="Payment status report"')
edit('pbms-react/src/workflows.jsx','aria-label="Beneficiary workflow"','aria-label="Beneficiary workflow" data-km-module="pbms" data-km-stage={tab===\'verification\'?\'Verification queue\':tab===\'payments\'?\'Payments\':\'Beneficiary lists\'}')
edit('pbms-react/src/workflows.jsx','aria-label="Confirm approval"','aria-label="Confirm approval" data-km-module="pbms" data-km-stage="Approval queue"')
# Visible branding only. Preserve domains, paths, email addresses and technical keys.
pattern=re.compile(r'\bNigeria[\s-]*G2P\b(?![.\w-])',re.I)
changed=[]
for folder in ['registration-ui','persona-ui/src','sitewide-ui','pbms-react/src','knowledge']:
 for p in (ROOT/folder).rglob('*'):
  if p.suffix not in ['.html','.jsx','.js','.css','.json','.csv'] or 'audit-' in p.name:continue
  old=p.read_text(encoding='utf-8');new=pattern.sub('NSIPA',old)
  if new!=old:p.write_text(new,encoding='utf-8');changed.append(str(p.relative_to(ROOT)))
print(json.dumps({'branding_files':changed}))
