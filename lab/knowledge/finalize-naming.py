from pathlib import Path
import re,shutil
src=Path(__file__).resolve().parents[1]
for name in ['add-local-guides.py','build-documentation-pack.py']:
 p=src/'knowledge'/name;s=p.read_text();p.write_text(s.replace('NigeriaG2P','NSIPA'))
p=src/'knowledge/help.js';s=p.read_text();s=s.replace(r'docs\.openg2p\.org|nigeriag2p\.com|github\.com',r'docs\.openg2p\.org|nigeriag2p\.com|g2p\.wverve\.in|github\.com');p.write_text(s)
shutil.copy2(p,'/opt/openg2p-lab/branding/knowledge-help.js')
# Keep library text readable even when a shared card style changes later.
rule='\n[data-analytics-library] details.card p,[data-analytics-library] details.card li,[data-analytics-library] details.card summary{white-space:normal;overflow:visible;text-overflow:clip;-webkit-line-clamp:unset;max-height:none;height:auto;overflow-wrap:anywhere}\n'
for p in [src/'knowledge/experience.css',Path('/opt/openg2p-lab/registration/static/experience.css')]:
 s=p.read_text()
 if '[data-analytics-library] details.card p' not in s:p.write_text(s+rule)
print('Source generators, reference links and library text styles aligned.')
