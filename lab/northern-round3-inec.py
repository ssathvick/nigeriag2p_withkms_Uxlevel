import requests
from pathlib import Path
import subprocess
p=Path('territory-data/raw/northern-round3-inec2023.pdf')
u='https://www.inecnigeria.org/wp-content/uploads/2024/02/2023-GENERAL-ELECTION-REPORT-1.pdf'
r=requests.get(u,timeout=45);r.raise_for_status();p.write_bytes(r.content)
subprocess.run(['pdftotext','-layout',str(p),str(p.with_suffix('.txt'))],check=True)
print(len(r.content),'bytes')

