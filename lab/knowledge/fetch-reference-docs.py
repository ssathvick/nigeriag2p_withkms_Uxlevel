from pathlib import Path
from urllib.request import urlopen
from concurrent.futures import ThreadPoolExecutor
import re,json,hashlib
root=Path('knowledge/upstream-docs');s=(root/'SUMMARY.md').read_text(encoding='utf-8');paths=re.findall(r'\]\(([^)]+\.md)\)',s)
selected=[]
feature=['unified-registry-model','change-management-and-approval-workflow','audit-ability-and-trace-ability','documents','ingestion-pipeline','version-history','registry-intake','consent-aware-data-sharing','deduplication','rbac-roles-and-permissions','export-register-data']
legacy=['create-an-individual-registrant','create-a-group-and-add-individual-registrants-to-the-group','configure-id-types','configure-relationships','import-csv-file-to-registry-module','configure-proxy-means-test','verify-eligibility-of-enrolled-registrants','deduplicate-registrants','enrol-registrants-into-program','create-program-fund','create-cycle-manager-for-a-program','multi-stage-approval','approve-entitlements','prepare-entitlements','map-program-to-self-service-portal-form','configure-notification-manager','customize-the-odk-importer-configuration-based-on-the-odk-form-fields','import-social-registry-data-into-pbms']
for path in paths:
 stem=Path(path).stem
 if '/registry/features/' in path and stem in feature:selected.append(path)
 elif '/pbms/_archive/previous-generation/' in path and stem in legacy:selected.append(path)
 elif path.startswith('pbms/features/') and stem in ['rule-driven-processing','dual-cycle-management','verification-workflows','controlled-list-management','reconciliation-with-sponsor-bank','reporting-and-dashboards']:selected.append(path)
 elif '/approval-workflow-engine/' in path and stem in ['functional-specifications','scenarios','segregation-of-duties','reassign-task','sla-escalation']:selected.append(path)
 elif '/master-data-service/catalogue/' in path and stem in ['concepts','geography','change-control','ui']:selected.append(path)
 elif '/partner-management/' in path and stem in ['functional-specifications','integration']:selected.append(path)
 elif path.startswith('consent-management/design/') and stem in ['consent-lifecycle','verification-and-enforcement','partner-onboarding-and-policy']:selected.append(path)
 elif '/identity-and-access-management/staff-ui/' in path and stem=='requirements':selected.append(path)
 elif 'importing-dashboards-on-the-superset-ui' in path:selected.append(path)
selected=list(dict.fromkeys(selected))
def fetch(path):
 url='https://raw.githubusercontent.com/OpenG2P/openg2p-documentation/latest/'+path
 try:
  b=urlopen(url,timeout=30).read();key=hashlib.sha256(path.encode()).hexdigest()[:12];(root/(key+'.md')).write_bytes(b)
  return dict(path=path,file=key+'.md',url='https://github.com/OpenG2P/openg2p-documentation/blob/latest/'+path,sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
 except Exception as e:return dict(path=path,error=str(e))
with ThreadPoolExecutor(max_workers=8)as pool:items=list(pool.map(fetch,selected))
(root/'manifest.json').write_text(json.dumps(items,indent=2),encoding='utf-8');print(json.dumps({'fetched':sum('file'in x for x in items),'failed':[x for x in items if 'error'in x]},indent=2))
for i,x in enumerate(items):
 if 'file'not in x:continue
 t=(root/x['file']).read_text(encoding='utf-8');t=re.split(r'# Agent Instructions',t)[0];t=re.sub(r'<figure>.*?</figure>','',t,flags=re.S);t=re.sub(r'!\[[^\]]*\]\([^)]*\)','',t)
 if i<26:print('\nDOC',i,x['path'],'\n',t[:3600])
