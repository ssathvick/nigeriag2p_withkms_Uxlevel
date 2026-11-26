"""Staff-only, version-specific evidence in the KMS editorial workspace."""
import hashlib
import json
import re
from collections import Counter
from urllib.parse import urlencode
from flask import abort, g, redirect, request

RUBRICS = {
    'field': [('Meaning and purpose',25),('Value or selection',35),('Format and limits',20),('Unknown or invalid value',20)],
    'screen': [('Role and starting state',20),('Controls in task order',35),('Outcome and handoff',25),('Recovery',20)],
    'workflow': [('Entry and exit',20),('Roles and sequence',30),('Evidence and handoffs',30),('Returns and related tasks',20)]
}
# Provisional dependencies curated from the linked pilot articles, not canonical platform IDs.
DEPENDENCIES = {
    'pbms.approval-comment': ('pbms-approval-comment','pbms-finance','pbms-flow-journey','pbms-audit','pbms-ceo'),
    'registry.return': ('register-returned-intake','register-journey','register-submission-detail','register-intake-queue'),
    'imports.return': ('imports-return-note','imports-journey'),
    'pbms.sponsor-routing': ('pbms-sponsor-routing','pbms-flow-open','pbms-flow-journey')
}
CALIBRATION = ('register-consent-answer','register-member-age','imports-return-note','pbms-approval-comment',
               'register-intake-queue','register-returned-intake','pbms-finance','register-journey',
               'imports-journey','pbms-flow-journey')
DDL = """
CREATE TABLE IF NOT EXISTS km_governance_events (
 id INTEGER PRIMARY KEY, article INTEGER NOT NULL, version INTEGER NOT NULL, kind TEXT NOT NULL,
 actor TEXT NOT NULL, at TEXT NOT NULL, detail TEXT NOT NULL);
CREATE INDEX IF NOT EXISTS km_gov_article ON km_governance_events(article,version,kind);
CREATE UNIQUE INDEX IF NOT EXISTS km_gov_score ON km_governance_events(article,version,actor) WHERE kind='score';
CREATE UNIQUE INDEX IF NOT EXISTS km_gov_ai ON km_governance_events(article,version,detail) WHERE kind='ai';
CREATE TABLE IF NOT EXISTS km_change_cases (
 id INTEGER PRIMARY KEY, dependency TEXT NOT NULL, description TEXT NOT NULL, actor TEXT NOT NULL, at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS km_change_targets (
 change_id INTEGER NOT NULL, article INTEGER NOT NULL, version INTEGER NOT NULL,
 PRIMARY KEY(change_id,article));
"""
def digest(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def linked_keys(row):
    slug=row['slug'].removeprefix('context-')
    data=json.loads(row['draft'])
    keys=[key for key,slugs in DEPENDENCIES.items() if slug in slugs]
    if data.get('context_key'): keys.append(data['context_key'])
    keys.extend(data.get('review_dependencies',[]))
    return sorted(set(keys))

def score_result(level, marks):
    rubric=RUBRICS[level]
    if len(marks)!=len(rubric) or any(m not in ('0','1','2','3','NA') for m in marks):
        raise ValueError('Select a score or Not Assessable for every criterion.')
    weight=sum(w for (_,w),m in zip(rubric,marks) if m!='NA')
    return round(100*sum(w*int(m) for (_,w),m in zip(rubric,marks) if m!='NA')/(3*weight),1) if weight else None

def normal(text):
    return ' '.join(re.findall(r'\w+', text.casefold()))

def preflight(row, peers, authority_check):
    data=json.loads(row['draft'])
    body=' '.join(data.get(k,'') for k in ('purpose','steps','requirements','next_step','issues'))
    issues=[]
    if authority_check(data) and not data.get('authority_reference'):
        issues.append(('Source gap','Record the controlling source for policy review.'))
    patterns=[('Boilerplate',r'\b(?:lorem ipsum|tbd|todo|insert (?:text|instructions) here|follow (?:the )?(?:standard|approved) procedure)\b'),
              ('Terminology',r'\b(?:revalidate|super admin|first level validator)\b')]
    for name,pattern in patterns:
        match=re.search(pattern,body+' '+data.get('title',''),re.I)
        if match: issues.append((name,'Check this wording against the approved terminology or procedure: '+match.group()))
    purpose=normal(data.get('purpose',''))
    matches=[str(p['id']) for p in peers if p['id']!=row['id'] and purpose and
             normal(json.loads(p['draft']).get('purpose',''))==purpose]
    if matches: issues.append(('Duplicate wording','Identical purpose in guide(s) '+', '.join(matches)+'. Check whether the overlap is intentional.'))
    tokens=set(normal(body).split())
    if len(tokens)>=12:
        similar=[]
        for peer in peers:
            if peer['id']==row['id'] or str(peer['id']) in matches:continue
            other=json.loads(peer['draft'])
            if other.get('module')!=data.get('module'):continue
            words=set(normal(' '.join(other.get(k,'') for k in ('purpose','steps','requirements','next_step','issues'))).split())
            if len(tokens & words)/len(tokens | words)>=0.85:similar.append(str(peer['id']))
        if similar:issues.append(('Near-duplicate wording','Compare overlapping wording with guide(s) '+', '.join(similar)+'.'))
    return issues

def text_units(data):
    units=[]
    for field in ('purpose','steps','requirements','next_step','issues'):
        for line in re.split(r'\n+|(?<=[.!?])\s+',data.get(field,'')):
            if line.strip():units.append({'id':len(units)+1,'field':field,'text':line.strip()})
    return units

def validate_report(row, report):
    """Require a finding for every text unit of the exact stored draft."""
    def need(value, message):
        if not value: raise ValueError(message)
    def text(value):
        return isinstance(value,str) and bool(value.strip())
    err='Invalid independent review evidence.'
    need(isinstance(report,dict),err)
    need(report.get('slug')==row['slug'] and report.get('version')==row['version'] and
         report.get('digest')==digest(row['draft']), 'The report belongs to a different guide or version.')
    need(all(text(report.get(k)) for k in ('prompt','prompt_version','model','at','instructional','technical','policy','verdict')),err)
    packet=report.get('packet')
    need(isinstance(packet,dict) and isinstance(packet.get('sources'),dict) and packet['sources'],err)
    need(all(isinstance(v,dict) and text(v.get('reference')) and text(v.get('text')) for v in packet['sources'].values()),err)
    data=json.loads(row['draft'])
    units=text_units(data)
    need(units and units==packet.get('units'),'The input snapshot must cover each current text unit.')
    findings=report.get('findings')
    need(isinstance(findings,list) and len(findings)==len(units),err)
    ids=set()
    for f in findings:
        need(isinstance(f,dict) and type(f.get('id')) is int and 1<=f['id']<=len(units) and f['id'] not in ids,err)
        need(text(f.get('finding')) and f.get('status') in ('supported','partial','unsupported'),err)
        refs=f.get('sources');need(isinstance(refs,list) and all(isinstance(ref,str) and ref in packet['sources'] for ref in refs),err)
        need(f['status']!='supported' or refs,err)
        ids.add(f['id'])
    return report

def record(c,row,kind,actor,at,detail):
    c.execute('INSERT INTO km_governance_events(article,version,kind,actor,at,detail) VALUES(?,?,?,?,?,?)',
              (row['id'],row['version'],kind,actor,at,json.dumps(detail,sort_keys=True,ensure_ascii=False)))

def visible_events(events,actor):
    counts=Counter((e['article'],e['version']) for e in events if e['kind']=='score')
    return [e for e in events if e['kind']!='score' or e['actor']==actor or counts[e['article'],e['version']]>=2]

def install(r,bp,require,permissions,authority_check):
    with r.db() as c: c.executescript(DDL)
    root=r.PREFIX+'/knowledge/admin'
    def rows():
        return r.rows("SELECT id,slug,version,draft,status,updated FROM km_articles ORDER BY id")
    def detail_url(aid): return root+'/'+str(aid)+'/checks'
    def events(aid=None):
        sql='SELECT * FROM km_governance_events'
        result=r.rows(sql+(' WHERE article=?' if aid else '')+' ORDER BY id DESC',(aid,) if aid else ())
        for e in result:e['detail']=json.loads(e['detail'])
        return visible_events(result,g.user['sub'])
    @bp.get(root+'/register')
    def governance_register():
        require('edit')
        query=request.args.get('q','').strip().casefold()
        dep=request.args.get('dependency','').strip()
        level=request.args.get('level','')
        scope=request.args.get('scope','')
        if len(query)>160 or len(dep)>160 or level not in ('',*RUBRICS) or scope not in ('','calibration','ai'):
            abort(400,'Invalid register filter.')
        ev=events()
        evidence=Counter((e['article'],e['version'],e['kind']) for e in ev)
        items=[]
        for a in rows():
            d=json.loads(a['draft']);keys=linked_keys(a)
            if level and level!=d.get('help_level'): continue
            if dep and dep not in keys: continue
            if scope=='calibration' and a['slug'].removeprefix('context-') not in CALIBRATION: continue
            if scope=='ai' and not evidence[a['id'],a['version'],'ai']: continue
            hay=' '.join([a['slug'],d['title'],d['stage'],d['module'],*keys]).casefold()
            if query and not all(word in hay for word in query.split()): continue
            items.append(dict(id=a['id'],version=a['version'],title=d['title'],module=d['module'],stage=d['stage'],
                              level=d.get('help_level','reference'),status=a['status'],updated=a['updated'],dependencies=keys,
                              ai=evidence[a['id'],a['version'],'ai'],scores=evidence[a['id'],a['version'],'score']))
        cases=r.rows('SELECT * FROM km_change_cases ORDER BY id DESC')
        if request.args.get('export')=='json':
            ids={i['id'] for i in items}
            return {'articles':items,'records':[e for e in ev if e['article'] in ids],
                    'changes':[dict(case,targets=r.rows('SELECT article,version FROM km_change_targets WHERE change_id=? ORDER BY article',(case['id'],))) for case in cases if not dep or case['dependency']==dep]}
        return r.page('knowledge-register.html',items=items,query=query,dep=dep,level=level,scope=scope,cases=cases,perms=permissions())
    @bp.get(root+'/<int:aid>/checks/input')
    def review_input(aid):
        require('edit')
        row=r.one('SELECT slug,version,draft FROM km_articles WHERE id=?',(aid,))
        if not row:abort(404)
        data=json.loads(row['draft'])
        response=r.app.json.response({'slug':row['slug'],'version':row['version'],'digest':digest(row['draft']),
            'article':data,'units':text_units(data)})
        response.headers['Content-Disposition']=f'attachment; filename="guide-{aid}-v{row["version"]}-review-input.json"'
        return response
    @bp.get(root+'/<int:aid>/checks')
    def guide_checks(aid):
        require('edit')
        row=r.one('SELECT * FROM km_articles WHERE id=?',(aid,))
        if not row: abort(404)
        d=json.loads(row['draft'])
        assessments=events(aid)
        current=[e for e in assessments if e['version']==row['version']]
        cases=r.rows('SELECT c.*,t.version FROM km_change_cases c JOIN km_change_targets t ON t.change_id=c.id WHERE t.article=? ORDER BY c.id DESC',(aid,))
        return r.page('knowledge-checks.html',article=row,data=d,keys=linked_keys(row),rubric=RUBRICS.get(d.get('help_level'),[]),
            issues=preflight(row,[p for p in rows() if p['status']!='archived'],authority_check),events=assessments,cases=cases,perms=permissions(),
            already=any(e['kind']=='score' and e['actor']==g.user['sub'] for e in current),
            can_reconcile=sum(e['kind']=='score' for e in current)>=2)
    @bp.post(root+'/<int:aid>/checks')
    def save_check(aid):
        require('review')
        kind=request.form.get('kind')
        if kind not in ('score','reconcile','impact'): abort(400)
        actor=g.user['sub'];note=request.form.get('note','').strip()
        if not 4<=len(note)<=1500:abort(400,'Give a review finding or reconciliation reason (4–1500 characters).')
        with r.db() as c:
            c.execute('BEGIN IMMEDIATE')
            row=c.execute('SELECT * FROM km_articles WHERE id=?',(aid,)).fetchone()
            if not row: abort(404)
            if str(row['version'])!=request.form.get('version'):abort(409,'Reload the changed article version.')
            if row['author']==actor:abort(403,'A different staff member must review this guide.')
            detail={'note':note}
            previous=c.execute("SELECT actor FROM km_governance_events WHERE article=? AND version=? AND kind='score'",(aid,row['version'])).fetchall()
            if kind=='score':
                if any(s['actor']==actor for s in previous) or len(previous)>=2: abort(409,'The reviewer score is already recorded or this pair is complete.')
                level=json.loads(row['draft']).get('help_level')
                if level not in RUBRICS: abort(400,'Choose a guidance level in the editor first.')
                marks=request.form.getlist('mark')
                try: value=score_result(level,marks)
                except ValueError as exc:abort(400,str(exc))
                detail.update(level=level,marks=marks,percentage=value,rubric='swift-pilot-1',criteria=RUBRICS[level])
            if kind=='reconcile' and len(previous)!=2: abort(409,'Two independent scores are required.')
            if kind=='impact':
                case=request.form.get('change','')
                target=c.execute('SELECT version FROM km_change_targets WHERE change_id=? AND article=?',(case,aid)).fetchone()
                if not target:abort(400,'Choose a change affecting this guide.')
                detail.update(change=int(case),affected_version=target['version'])
            duplicate=c.execute('SELECT id FROM km_governance_events WHERE article=? AND version=? AND kind=? AND actor=? AND detail=?',
                (aid,row['version'],kind,actor,json.dumps(detail,sort_keys=True,ensure_ascii=False))).fetchone()
            if not duplicate:record(c,row,kind,actor,r.stamp(),detail)
        return redirect(detail_url(aid))
    @bp.post(root+'/<int:aid>/checks/report')
    def attach_check(aid):
        require('review')
        attachment=request.files.get('report')
        if not attachment:abort(400,'Choose the independent review JSON file.')
        raw=attachment.stream.read(192001)
        if len(raw)>192000:abort(400,'Keep the review report under 192 KB.')
        with r.db() as c:
            c.execute('BEGIN IMMEDIATE')
            row=c.execute('SELECT * FROM km_articles WHERE id=?',(aid,)).fetchone()
            if not row:abort(404)
            if str(row['version'])!=request.form.get('version'):abort(409,'Reload the changed article.')
            if row['author']==g.user['sub']:abort(403,'A different reviewer must attach the check.')
            try: report=validate_report(row,json.loads(raw))
            except (ValueError,RecursionError) as exc:abort(400,str(exc))
            previous=c.execute("SELECT id FROM km_governance_events WHERE article=? AND version=? AND kind='ai' AND detail=?",
                (aid,row['version'],json.dumps(report,ensure_ascii=False,sort_keys=True))).fetchone()
            if not previous:record(c,row,'ai',g.user['sub'],r.stamp(),report)
        return redirect(detail_url(aid))
    @bp.post(root+'/register/change')
    def open_change():
        require('review')
        dep=request.form.get('dependency','').strip()
        note=request.form.get('description','').strip()
        if not 4<=len(note)<=1500 or not dep or len(dep)>160:abort(400,'Enter the dependency and a description.')
        with r.db() as c:
            c.execute('BEGIN IMMEDIATE')
            targets=[row for row in c.execute("SELECT id,slug,version,draft FROM km_articles WHERE status!='archived'") if dep in linked_keys(row)]
            if not targets:abort(400,'No current guides map to this exact dependency.')
            same=c.execute('SELECT id FROM km_change_cases WHERE dependency=? AND description=? AND actor=? ORDER BY id DESC LIMIT 1',
                           (dep,note,g.user['sub'])).fetchone()
            if same:
                old={(t['article'],t['version']) for t in c.execute('SELECT article,version FROM km_change_targets WHERE change_id=?',(same['id'],))}
                if old=={(t['id'],t['version']) for t in targets}:return redirect(root+'/register?'+urlencode({'dependency':dep}))
            change=c.execute('INSERT INTO km_change_cases(dependency,description,actor,at) VALUES(?,?,?,?)',(dep,note,g.user['sub'],r.stamp())).lastrowid
            c.executemany('INSERT INTO km_change_targets VALUES(?,?,?)',[(change,t['id'],t['version']) for t in targets])
        return redirect(root+'/register?'+urlencode({'dependency':dep}))

