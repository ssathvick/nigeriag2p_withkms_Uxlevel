from pathlib import Path
import shutil,datetime
src=Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/client-concerns/registry-presentation.css');dest=Path('/opt/openg2p-lab/branding/registry-presentation.css');shutil.copy2(dest,dest.with_name('registry-presentation.css.before-enumeration-'+datetime.datetime.now().strftime('%Y%m%d%H%M%S')));shutil.copy2(src,dest);print('Published scoped household field layout')
