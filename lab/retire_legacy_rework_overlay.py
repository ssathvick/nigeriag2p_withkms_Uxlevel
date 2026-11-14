import datetime,re,shutil,subprocess
from pathlib import Path
src=Path(__file__).parent/'client-concerns/registry-presentation.js';text='\n'.join(line for line in src.read_text().splitlines() if not line.strip().startswith('if(item?.remarks'))+'\n';src.write_text(text)
backup=Path('/opt/openg2p-lab/registration/native-meeting-backups')/('overlay-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));backup.mkdir(parents=True,mode=0o700)
target=Path('/opt/openg2p-lab/branding/registry-presentation.js');shutil.copy2(target,backup/'registry-presentation.js');target.write_text(text)
snippet=Path('/etc/nginx/snippets/iqs-brand.conf');shutil.copy2(snippet,backup/'iqs-brand.conf');s=snippet.read_text();s=re.sub(r'registry-presentation\.js(?:\?[^"\s]*)?', 'registry-presentation.js?v=native-meeting-20261112',s);snippet.write_text(s)
subprocess.run(['nginx','-t'],check=True,capture_output=True);subprocess.run(['systemctl','reload','nginx'],check=True);print('Retired obsolete rejection-as-correction overlay; native feedback and history own the screen.')
