import requests,json
from bs4 import BeautifulSoup
from pathlib import Path
p=Path('territory-data/raw');s=BeautifulSoup((p/'naltf-senators.html').read_text(),'html.parser')
e=s.select_one('.eael-filter-gallery-container');print(str(e)[:4500]);print('templates',[(a.get('type'),len(a.text),a.text[:80]) for a in s.select('script') if 'Akpabio' in a.text or 'Ngwu' in a.text])
r=requests.get('https://billtracker.naltf.gov.ng/api/bills',timeout=45);print('bills',r.status_code,r.text[:1800]);(p/'naltf-bills.json').write_text(r.text)
