from pathlib import Path
p=Path('jos_connected.py');s=p.read_text().replace("%s,%s,'NGN','0000000000',%s,%s,%s,0", "%s,%s,'NGN',%s,%s,%s,%s,0").replace("('SAMPLE JOS SIMULATOR ONLY',acc,acc.lower()", "('SAMPLE JOS SIMULATOR ONLY',acc,'0000710000' if acc==TREASURY else '0000710'+x['id'][-3:],acc.lower()")
p.write_text(s)
