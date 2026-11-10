from pathlib import Path
import shutil,datetime,subprocess
src=Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab');root=Path('/opt/openg2p-lab/registration');backup=Path('/opt/openg2p-lab/beneficiary-extra/backups')/('handoff-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));backup.mkdir()
path=root/'registration_app.py';shutil.copy2(path,backup/path.name);text=path.read_text()
if "g.session['login']['beneficiary_profile']" not in text:
 text=text.replace(" g.session['login']['grievances']=request.args.get('grievances')=='1'"," g.session['login']['grievances']=request.args.get('grievances')=='1'\n g.session['login']['beneficiary_profile']=mode=='beneficiary' and request.args.get('profile')=='1'")
 text=text.replace(" if flow.get('jos'):return redirect", " if flow.get('beneficiary_profile'):return redirect(PREFIX+'/profile')\n if flow.get('jos'):return redirect")
 path.write_text(text)
for path in [src/'registration-ui/profile.html',root/'templates/profile.html']:
 text=path.read_text()
 if 'Back to beneficiary registries' not in text:
  text=text.replace('<h1 data-i18n="register">','<p><a href="{{\'https://g2p-beneficiary.wverve.in\' if \'wverve.in\' in base|string else \'https://beneficiary.nigeriag2p.com\'}}/selfservice/en/registries">← Back to beneficiary registries</a></p><h1 data-i18n="register">');path.write_text(text)
subprocess.run(['systemctl','restart','iqs-registration'],check=True)
print('Registration intent and return link deployed; backup:',backup)
