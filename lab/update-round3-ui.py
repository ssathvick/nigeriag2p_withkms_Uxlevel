from pathlib import Path
p=Path('persona-ui/src/representatives.jsx');s=p.read_text()
if "from './representative-provenance.jsx'" not in s:s=s.replace('const nf=',"import {ConstituencyEvidence,ArchivedRepresentatives} from './representative-provenance.jsx';\nconst nf=")
s=s.replace(' <RepresentativeActivity representative={r}/>',' <ConstituencyEvidence record={r}/><RepresentativeActivity representative={r}/>')
s=s.replace('<th>Assembly entries</th><th>Qualification</th>','<th>Assembly entries</th><th>Missing constituency labels</th><th>Qualification</th>')
s=s.replace("<td>{s.assembly_entries||'Unavailable / not applicable'}</td><td>{s.assembly_status}</td>","<td>{s.assembly_entries||'Unavailable / not applicable'}</td><td>{s.assembly_entries?s.constituencies_unverified:'Not applicable'}</td><td>{s.assembly_status}</td>")
s=s.replace('Other assembly rosters and local council heads remain unverified.','Full membership lists and local council heads remain incomplete. {dataset.coverage.assembly_seats_unverified} loaded assembly entries still lack a verified constituency label.')
s=s.replace('<section className="ti-panel"><h2>How to read this performance view</h2>','<ArchivedRepresentatives members={dataset.archived_members}/><section className="ti-panel"><h2>How to read this performance view</h2>')
p.write_text(s)
