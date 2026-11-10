from pathlib import Path
p=Path('build-territory-data.py');s=p.read_text().replace("add_state_reports(data,RAW)","add_state_reports(data,RAW)\nfrom territory_representatives import add_representatives\nadd_representatives(data,RAW)");p.write_text(s)
