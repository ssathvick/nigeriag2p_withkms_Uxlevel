from pathlib import Path
import shutil,hashlib,re,datetime
root=Path('/opt/openg2p-lab');src=Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/persona-ui/dist/site.js');backup=root/'home-navigation-backups'/datetime.datetime.now().strftime('%Y%m%d-%H%M%S');backup.mkdir(parents=True)
shutil.copy2(root/'branding/site.js',backup/'site.js');shutil.copy2(src,root/'branding/site.js');digest=hashlib.sha256(src.read_bytes()).hexdigest()[:12]
for name in ('public-home','home'):
 p=root/name/'index.html';shutil.copy2(p,backup/(name+'-index.html'));s=p.read_text();s=re.sub(r'/iqs-brand/site\.js(?:\?v=[^" ]+)?',f'/iqs-brand/site.js?v=services-{digest}',s);s=s.replace('<a href="/registration/workspace">Registration workspace</a>','<a href="https://g2p-register.wverve.in/en">Master Registry</a>');p.write_text(s)
print('Published simplified home navigation',digest)
