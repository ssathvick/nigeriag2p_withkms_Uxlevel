from pathlib import Path
import shutil,datetime,subprocess
src=Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab');root=Path('/opt/openg2p-lab/registration');backup=root/'geography-backups'/('map-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));backup.mkdir(mode=0o700)
shutil.copy2(root/'templates/geography.html',backup/'geography.html')
shutil.copy2(root/'nigeria_geography.py',backup/'nigeria_geography.py')
shutil.copy2(src/'nigeria_geography.py',root/'nigeria_geography.py')
for asset in ['geography-map.js','geography-map.css','nigeria-states.geojson']:
 if (root/'static'/asset).exists():shutil.copy2(root/'static'/asset,backup/asset)
 shutil.copy2(src/'registration-ui'/asset,root/'static'/asset)
shutil.copy2(src/'registration-ui/geography.html',root/'templates/geography.html')
subprocess.run(['systemctl','restart','iqs-registration.service'],check=True)
print('State map installed with recoverable file backup.')
