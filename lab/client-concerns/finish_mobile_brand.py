from pathlib import Path
import re,shutil
root=Path(__file__).resolve().parents[1]/'field-app'
p=root/'android/src/org/nigeriag2p/field/MainActivity.java';s=p.read_text();a=s.index(' void showSplash()');b=s.index('\n void set(',a)
s=s[:a]+''' void showSplash(){screen("Household Intake Form");body.addView(text("NSIPA Unified G2P",28));body.addView(text("Save a household draft offline. Upload the reviewed sample when connected. Server approval is a separate step.",19));button(body,"Open field workspace",()->home());}
'''+s[b:];p.write_text(s)
p=root/'android/test-instructions.html';s=p.read_text();s=re.sub(r'(?i)Nigeria[ -]*G2P','NSIPA',s);s=s.replace('G2P Field Demo','NSIPA Household Intake').replace('Version 0.6','Version 0.7').replace('8 November 2026','10 November 2026').replace('./nigeria-g2p-field-demo-v0.6.apk','./nsipa-household-intake-v0.7.apk');s=s.replace('Complete the other tabs with fictional data','Enter the household name and household head name in Home. Complete the other tabs with fictional data');s=s.replace('Optionally capture device GPS with permission or enter latitude and longitude','Optionally capture device GPS with permission (target accuracy: 50 metres, 30-second timeout) or enter latitude and longitude');p.write_text(s)
for home in ['home','public-home']:
 dest=Path('/opt/openg2p-lab')/home/'field-preview/android/index.html';shutil.copy2(p,dest)
