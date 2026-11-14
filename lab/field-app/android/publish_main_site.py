from pathlib import Path
import shutil,hashlib,re
src=Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/persona-ui/dist/site.js'); dest=Path('/opt/openg2p-lab/branding/site.js')
shutil.copy2(dest, dest.with_name('site.js.before-field-mobile'))
shutil.copy2(src,dest)
digest=hashlib.sha256(src.read_bytes()).hexdigest()[:12]
for name in ('public-home','home'):
 p=Path('/opt/openg2p-lab')/name/'index.html'; s=p.read_text();s=re.sub(r'/iqs-brand/site\.js\?v=[^" ]+',f'/iqs-brand/site.js?v=field-{digest}',s);p.write_text(s)
print('Updated site bundle',digest)
