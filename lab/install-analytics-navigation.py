from pathlib import Path
import shutil,datetime,json
src=Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab');root=Path('/opt/openg2p-lab')
backup=root/'registration/analytics-backups'/('navigation-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));backup.mkdir(mode=0o700)
targets=[(src/'persona-ui/dist/site.js',root/'branding/site.js'),(src/'persona-ui/dist/site-shell.js',root/'branding/site-shell.js'),(src/'persona-ui/dist/workspace.js',root/'registration/static/workspace.js')]
manifest=[]
for i,(source,target) in enumerate(targets):
 saved=backup/str(i)
 if target.exists():shutil.copy2(target,saved)
 manifest.append({'target':str(target),'saved':str(saved) if saved.exists() else None})
 shutil.copy2(source,target)
(backup/'manifest.json').write_text(json.dumps(manifest))
print('Service catalogue now links Analytics to the native workspace.')
