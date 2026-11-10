from pathlib import Path
import shutil,datetime,subprocess
src=Path(__file__).resolve().parent
backup=Path('/opt/openg2p-lab/backups')/('beneficiary-callback-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));backup.mkdir(mode=0o700)
for p in [Path('/etc/nginx/conf.d/iqs-dual-domain.conf'),src/'dual-domain/nginx-alias.conf']:
 shutil.copy2(p,backup/(p.parent.name+'-'+p.name));s=p.read_text()
 s=s.replace(' staff-portal $iqs_native_args_23_1;',' staff-portal $iqs_native_args_23_1;\n nigeria-beneficiary-portal $iqs_native_args_23_1;')
 s=s.replace(' location = /realms/staff/protocol/openid-connect/auth {',' location ~ ^/realms/(staff|beneficiary)/protocol/openid-connect/auth$ {')
 p.write_text(s)
subprocess.run(['nginx','-t'],check=True);subprocess.run(['systemctl','reload','nginx'],check=True);print('Beneficiary callback alias aligned; backup '+str(backup))
