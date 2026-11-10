from pathlib import Path
import re
s=Path('territory-data/raw/naltf-bills.js').read_text()
print('\n'.join(re.findall(r'.{0,110}(?:de\.get\(|fetch\(`${Nr}|getBills\().{0,200}',s))[:16000])
s=Path('territory-data/raw/naltf-senators.html').read_text()
for word in ['load-more','load_more','gallery_load','eael_gallery','gallery_items','data-total','data-settings']:
 print(word,[s[max(0,m.start()-100):m.start()+250] for m in list(re.finditer(word,s))[:4]])

