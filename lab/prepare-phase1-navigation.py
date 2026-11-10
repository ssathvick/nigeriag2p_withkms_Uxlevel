from pathlib import Path
root=Path(__file__).parent
p=root/'persona-ui/src/site.jsx'
s=p.read_text(encoding='utf-8')
old='<a href="/registration/workspace?demo=1">Client walkthrough</a>'
new=old+'<a href="/registration/phase1">Phase 1 sandbox</a><a href="/registration/phase1/portal">Public demo portal</a>'
if 'href="/registration/phase1"' not in s:
    if s.count(old)!=1:raise RuntimeError('Unexpected launcher layout; inspect before editing')
    p.write_text(s.replace(old,new),encoding='utf-8')
p=root/'sitewide-ui/index.html'
s=p.read_text(encoding='utf-8')
s=s.replace('src="/iqs-brand/site.js"','src="/iqs-brand/site.js?v=phase1-20261012"')
p.write_text(s,encoding='utf-8')
p=root/'persona-ui/src/shell.js'
s=p.read_text(encoding='utf-8')
anchor="if(identity)module="
new="if(isRoot&&location.pathname.startsWith('/registration/phase1'))module={title:'Phase 1 sandbox',description:'Fictional grievances, field delivery, agent certification and module walkthroughs.'};"+anchor
if "title:'Phase 1 sandbox'" not in s:
    if s.count(anchor)!=1:raise RuntimeError('Unexpected shared navigation; inspect before editing')
    p.write_text(s.replace(anchor,new),encoding='utf-8')
