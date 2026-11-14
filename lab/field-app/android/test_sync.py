from pathlib import Path
import subprocess, tempfile, xml.etree.ElementTree as ET
base=Path(__file__).resolve().parent
manifest=ET.parse(base/'AndroidManifest.xml').getroot()
ns='{http://schemas.android.com/apk/res/android}'
assert {p.attrib[ns+'name'] for p in manifest.findall('uses-permission')} == {'android.permission.INTERNET','android.permission.ACCESS_FINE_LOCATION'}
assert not manifest.findall('.//service') and not manifest.findall('.//receiver')
source='\n'.join(p.read_text() for p in (base/'src').rglob('*.java'))
for banned in ['.schedule(', 'setPersisted(', 'setPeriodic(', 'extends JobService', 'WorkManager', 'AlarmManager']:
    assert banned not in source, banned
activity=(base/'src/org/nigeriag2p/field/MainActivity.java').read_text()
assert activity.count('()->sync()')==1
assert 'scheduler.cancel(10441);scheduler.cancel(10442);' in activity
assert 'protected void onStop(){cancelLocation();if(activeUpload!=null)activeUpload.cancel();' in activity
cp=f"{base}/build/classes:/usr/share/java/com.android.json.jar:/usr/lib/android-sdk/platforms/android-23/android.jar"
with tempfile.TemporaryDirectory() as tmp:
    subprocess.run(['javac','-cp',cp,'-d',tmp,str(base/'SyncHarness.java')],check=True)
    subprocess.run(['java','-cp',tmp+':'+cp,'org.nigeriag2p.field.SyncHarness'],check=True,timeout=30)
print('PASS: source/manifest background-execution regression checks')
