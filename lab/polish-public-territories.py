from pathlib import Path
p=Path('collect-territory-sources.py');s=p.read_text().replace("'inec.pdf':'https://www.inecnigeria.org/wp-content/uploads/2024/02/2023-GENERAL-ELECTION-REPORT-1.pdf',",'');p.write_text(s)
p=Path('download-territory-layers.py');s=p.read_text();s=s[:s.index("for name,path in [('inec'")];p.write_text(s)
p=Path('persona-ui/src/territories.jsx');s=p.read_text().replace('<dialog ref={dialog} className="ti-dialog"','<dialog ref={dialog} aria-label="Measure provenance" className="ti-dialog"').replace('<p className="ti-muted">{filtered.length}', '<p className="ti-muted" role="status">{filtered.length}');p.write_text(s)
