import requests
from pathlib import Path
from bs4 import BeautifulSoup
u='https://radionigeriasouthsouth.gov.ng/ubth-cmd-seeks-legislative-action-on-substance-drug-abuse-as-edha-speaker-pays-visit/'
r=requests.get(u,timeout=25);r.raise_for_status();Path('territory-data/raw/edo-ubth-2026.html').write_text(r.text);s=BeautifulSoup(r.text,'html.parser');a=s.select_one('article') or s;print(a.get_text(' ',strip=True)[:10000])
