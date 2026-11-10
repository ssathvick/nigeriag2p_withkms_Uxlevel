import fitz
from pathlib import Path
p=Path('territory-data/raw/lagos-ledu-2025.pdf');doc=fitz.open(p)
for i,page in enumerate(doc):
 t=page.get_text()
 if ('capita' in t.lower() and i>15 and i<45) or ('Nominal GDP' in t and i>15):
  print('PAGE',i+1,t[:12000])
