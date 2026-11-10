import collections,json,pathlib,re,sqlite3,requests
root=pathlib.Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/knowledge')
db=sqlite3.connect('/opt/openg2p-lab/registration/intake.sqlite');db.row_factory=sqlite3.Row
rows=[dict(r) for r in db.execute('SELECT id,slug,module,stage,audience,published,published_version,draft,version,status FROM km_articles')]
(root/'context-audit-before.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
flags=[];lengths=collections.Counter();modules=collections.Counter()
for row in rows:
    if not row['published']:continue
    a=json.loads(row['published']);modules[a['module']]+=1
    for key in ['title','purpose','steps','requirements','next_step','issues']:
        text=a.get(key,'');lengths[len(text)]+=1
        for line in text.splitlines():
            if line and (re.search(r'(?:\.\.\.|…)\s*$',line) or len(line) in [120,160,180,200,240,250,300,400,500,600] or re.search(r'\b(?:and|or|the|a|an|to|for|of|with|that|which|this|these|by|from|in|is|are)\.?$',line,re.I)):
                flags.append({'id':row['id'],'slug':row['slug'],'module':a['module'],'stage':a['stage'],'key':key,'text':line,'length':len(line)})
print(json.dumps({'articles':len(rows),'published_modules':modules,'common_lengths':lengths.most_common(12),'suspicious':flags},ensure_ascii=False,indent=2))
