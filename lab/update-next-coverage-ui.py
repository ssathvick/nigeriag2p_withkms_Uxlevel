from pathlib import Path
p=Path('persona-ui/src/representatives.jsx');s=p.read_text()
s=s.replace("const nf=", "import RepresentativeActivity from './representative-activity.jsx';\nconst nf=")
s=s.replace("'State assembly entries · 9 states'","'Assembly entries · '+dataset.coverage.assembly_states+' states'")
s=s.replace('Assembly sources cover nine states, with partial Rivers coverage and unresolved seat labels.','Assembly sources cover {dataset.coverage.assembly_states} states, including partial rosters, dated reports and unresolved seat labels.')
s=s.replace('Publisher roster loaded; seat and tenure qualifications apply','Publisher evidence loaded; completeness and tenure qualifications apply')
start=s.index(' <section className="ti-panel"><h3>Documented activity</h3>');end=s.index('\n {[\'Governor\'',start)
s=s[:start]+' <RepresentativeActivity representative={r}/>'+s[end:]
s=s.replace('Verify officeholder with publisher ↗</a>','Verify officeholder with publisher ↗</a>{r.secondary_source_url&&<p><a href={r.secondary_source_url} target="_blank" rel="noreferrer">Additional official constituency source ↗</a></p>}{r.source_date&&<p>Source report: {r.source_date} · reference year {r.reference_year}. Later changes are not certified.</p>}')
s=s.replace('Missing evidence does not mean no work was done.</p></div>','Missing evidence does not mean no work was done. {dataset.coverage.activity_records} distinct activity reports are linked to {dataset.coverage.members_with_activity_evidence} people.</p></div>')
p.write_text(s)
