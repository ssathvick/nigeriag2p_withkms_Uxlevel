from pathlib import Path
p=Path('persona-ui/src/representatives.jsx');s=p.read_text();s=s.replace("const chambers=", "const sortName=s=>s.replace(/^(?:(?:sen|hon|rt|dr|mrs)\\.?[, ]*)+/i,'').trim();\nconst chambers=");s=s.replace('a.name.localeCompare(b.name)','sortName(a.name).localeCompare(sortName(b.name))');p.write_text(s)
