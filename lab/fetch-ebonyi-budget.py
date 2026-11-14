import requests
from pathlib import Path
import subprocess
p=Path('territory-data/raw/ebonyi-budget-2026.pdf');r=requests.get('https://ebonyistate.gov.ng/storage/documents/min-1-2026-approved-budgetpdf-1769898846.pdf',timeout=30);r.raise_for_status();p.write_bytes(r.content)
subprocess.run(['pdftotext','-f','1','-l','12',str(p),str(p.with_suffix('.txt'))],check=True);print(p.with_suffix('.txt').read_text()[:6000])
