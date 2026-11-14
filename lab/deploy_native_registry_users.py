import datetime,py_compile,shutil
from pathlib import Path
import subprocess
src=Path(__file__).parent;root=Path('/opt/openg2p-lab/registration');path=root/'registration_app.py';backup=root/'native-meeting-backups'/('users-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));backup.mkdir(parents=True,mode=0o700);shutil.copy2(path,backup/'registration_app.py');text=path.read_text()
text=text.replace("request.path != PREFIX+'/api/registry/offline-setup'", "request.path not in (PREFIX+'/api/registry/offline-setup',PREFIX+'/api/registry/users')")
if 'import native_registry_users' not in text:text=text.replace('import native_offline_setup\n','import native_registry_users\nnative_registry_users.install(os.sys.modules[__name__])\nimport native_offline_setup\n')
path.write_text(text);py_compile.compile(str(path),doraise=True);shutil.copy2(src/'native_registry_users.py',root/'native_registry_users.py');shutil.copy2(path,src/'registration_app.py');subprocess.run(['systemctl','restart','iqs-registration'],check=True);print('Native Registry staff directory deployed.')
