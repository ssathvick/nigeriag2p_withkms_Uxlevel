from pathlib import Path
from bs4 import BeautifulSoup
s=BeautifulSoup(Path('territory-data/raw/ngf-current.html').read_text(),'html.parser');a=s.find('a',string=lambda t:t and 'Abia State Governor' in t)
for parent in list(a.parents)[:6]:print(parent.name,parent.get('class'),parent.get_text(' ',strip=True)[:250])
s=BeautifulSoup(Path('territory-data/raw/osun-assembly.html').read_text(),'html.parser');e=s.select_one('.all-member-main-content');[x.decompose() for x in e.select('img')];print(str(e)[:2800])
s=BeautifulSoup(Path('territory-data/raw/ondo-assembly.html').read_text(),'html.parser');print('inline scripts',[(len(x.text),x.text[-1500:]) for x in s.select('script')][-3:])
