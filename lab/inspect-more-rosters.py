from pathlib import Path
from bs4 import BeautifulSoup
p=Path('territory-data/raw')
for key,find in [('ngf-current','Abia State Governor'),('kwara-assembly','YAKUBU')]:
 s=BeautifulSoup((p/(key+'.html')).read_text(),'html.parser');n=s.find(string=lambda t:t and find in t)
 print(key,str(n.parent.parent.parent)[:6500])
