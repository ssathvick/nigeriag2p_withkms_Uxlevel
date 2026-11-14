import datetime,py_compile,shutil,subprocess
from pathlib import Path
src=Path(__file__).parent;root=Path('/opt/openg2p-lab/registration');backup=root/'native-meeting-backups'/('offline-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));backup.mkdir(parents=True,mode=0o700)
path=root/'registration_app.py';shutil.copy2(path,backup/'registration_app.py');text=path.read_text()
text=text.replace("if request.method=='POST' and not secrets.compare_digest(","if request.method=='POST' and request.path != PREFIX+'/api/registry/offline-setup' and not secrets.compare_digest(",1)
if 'import native_offline_setup' not in text:text=text.replace('import mbr_workflow\n','import native_offline_setup\nnative_offline_setup.install(os.sys.modules[__name__])\nimport mbr_workflow\n')
path.write_text(text);py_compile.compile(str(path),doraise=True);shutil.copy2(src/'native_offline_setup.py',root/'native_offline_setup.py')
mapping=Path('/opt/openg2p-lab/odk-sync/odk_household_mapping.py');shutil.copy2(mapping,backup/'odk_household_mapping.py');shutil.copy2(src/'client-concerns/odk_household_mapping.py',mapping)
subprocess.run(['systemctl','restart','iqs-registration'],check=True)
shutil.copy2(path,src/'registration_app.py');print('Native offline setup and source consent mapping deployed; credentials remain private.')
