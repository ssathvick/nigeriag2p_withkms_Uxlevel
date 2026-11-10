import subprocess,xml.etree.ElementTree as E,re,time
adb='/mnt/h/Nigeria_Mosip/codex/openg2p-lab/field-app/android/tools/platform-tools/adb.exe'; b=[adb,'-P','5038','-s','6b8f8c38']
def cmd(*xs):return subprocess.check_output(b+list(xs),stderr=subprocess.STDOUT,timeout=15).decode('utf8','replace')
def tree():
 focus=cmd('shell','dumpsys','window'); assert 'org.nigeriag2p.field/org.nigeriag2p.field.MainActivity' in focus and 'mDreamingLockscreen=true' not in focus,'App not in foreground or phone locked'
 cmd('shell','uiautomator','dump','/sdcard/f-test.xml'); return E.fromstring(subprocess.check_output(b+['shell','cat','/sdcard/f-test.xml']))
def nodes(t,txt):return [e for e in t.iter('node') if e.get('text')==txt and e.get('package')=='org.nigeriag2p.field']
def tap_node(e):
 z=list(map(int,re.findall(r'\d+',e.get('bounds')))); assert len(z)==4 and z[3]>z[1];cmd('shell','input','tap',str((z[0]+z[2])//2),str((z[1]+z[3])//2));time.sleep(0.5)
def tap(txt):
 t=tree(); a=nodes(t,txt); assert a,'Missing '+txt; tap_node(a[-1] if txt in ['Plateau'] else a[0])
def enter_first_empty(value):
 t=tree(); a=[e for e in t.iter('node') if e.get('package')=='org.nigeriag2p.field' and e.get('class')=='android.widget.EditText' and (e.get('text') or '') in ('','Sample only')]; assert a,'Missing empty input';tap_node(a[0]);cmd('shell','input','text',value);cmd('shell','input','keyevent','4')
tap('＋ New sample visit');enter_first_empty('SAMPLE003');tap('Select');tap('Yes');tap('Area');tap('Choose State / FCT');tap('Search State / FCT');cmd('shell','input','text','Plateau');cmd('shell','input','keyevent','4');tap('Plateau');tap('Choose Local government area');tap('Jos North');tap('Choose Ward');tap('Gangare');tap('Home');enter_first_empty('SAMPLE-RECONNECT-03');enter_first_empty('3');enter_first_empty('1');tap('Select');tap('Owned');tap('Needs');tap('Select');tap('Agriculture');tap('Select');tap('Food');tap('Review');tap('Save and send for supervisor review');enter_first_empty('246810');t=tree();assert nodes(t,'Approve and finalize offline'),'Missing review button';print('Fictional sample ready for offline approval; network unchanged.',flush=True)

