from pathlib import Path
from PIL import Image,ImageDraw
p=Path('/mnt/h/Nigeria_Mosip/codex/output/ooru-meeting-audit/household-detail')
for prefix in ['online','offline']:
 files=sorted(p.glob(prefix+'-*.jpg'))
 for start in range(0,len(files),8):
  sheet=Image.new('RGB',(1800,1100),'white');d=ImageDraw.Draw(sheet)
  for j,f in enumerate(files[start:start+8]):
   im=Image.open(f);im.thumbnail((900,250));x=j%2*900;y=j//2*275;sheet.paste(im,(x,y+20));d.text((x,y),f.name,fill='black')
  sheet.save(p/f'{prefix}-sheet-{start//8+1}.jpg')
