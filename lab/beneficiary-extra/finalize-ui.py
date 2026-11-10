from pathlib import Path
p=Path(__file__).parent/'main.jsx';s=p.read_text(encoding='utf-8-sig')
s=s.replace('pattern="LAB-[A-Za-z0-9-]{4,32}"',r'pattern="LAB-[A-Za-z0-9\x2d]{4,32}"')
s=s.replace(".filter(([k])=>!['strategy_id'].includes(k))",".filter(([k,v])=>k!=='strategy_id'&&v!==null&&v!=='')")
s=s.replace('<dt>{clean(k)}</dt>',"<dt>{k==='fa_type'?'Account type':clean(k)}</dt>")
p.write_text(s)
