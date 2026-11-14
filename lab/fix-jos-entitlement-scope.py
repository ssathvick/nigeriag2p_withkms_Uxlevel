from pathlib import Path
p=Path('jos_connected.py');s=p.read_text().replace("key+'-ENT-C01'", "'IQS-REG-APP-'+key+'-ENT-C01'");p.write_text(s)
