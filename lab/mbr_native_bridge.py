"""Runtime ownership and native-record adapters for the integrated registry workflow."""
import json
import uuid
from flask import abort, g, request, redirect
from psycopg2 import sql
from psycopg2.extras import Json, RealDictCursor
# Kept separate from the HTTP application so migration can also run against restored databases.
from mbr_native_migration import DDL, canonical, digest


def actor_ids(cur,user):
    cur.execute('SELECT alias FROM g2p_mbr_actor_alias WHERE actor_id=%s',(user['sub'],))
    return [user['sub'],*[x['alias'] for x in cur.fetchall()]]


def mapped(cur,sid):
    cur.execute('SELECT * FROM g2p_mbr_native_map WHERE submission_id=%s',(str(sid),))
    row=cur.fetchone();return dict(row) if row else None


def assigned(cur,record,user):
    mapping=mapped(cur,record['id'])
    if not mapping or mapping['metadata'].get('assignment_released'):return True
    tasks=[t for t in mapping['metadata']['tasks'] if t['stage_order']==record['stage'] and t['status'] in ['open','claimed'] and t.get('kind')!='observer']
    if not tasks:return True
    aliases=actor_ids(cur,user)
    return any(t['assignee'] in aliases for t in tasks)


def enrich(cur,record):
    mapping=mapped(cur,record['id'])
    if not mapping:return record
    meta=mapping['metadata'];ids=meta['attempt_ids']
    cur.execute("SELECT body FROM g2p_mbr_source_archive WHERE source_db='awe' AND source_table='approval_request' AND body->>'id'=ANY(%s) ORDER BY body->>'created_at'",(ids,))
    attempts=[x['body'] for x in cur.fetchall()]
    cur.execute("SELECT body FROM g2p_mbr_source_archive WHERE source_db='awe' AND source_table='approval_task' AND body->>'request_id'=ANY(%s) ORDER BY body->>'created_at'",(ids,))
    tasks=[x['body'] for x in cur.fetchall()]
    record['migration']={'native_kind':mapping['native_kind'],'native_key':mapping['native_key'],
                         'original_status':meta['original']['approval_status'], 'original_draft_status':meta['original'].get('draft_status'),
                         'old_values_available':meta['old_values_available'],
                         'attempts':[{'id':x['id'],'status':x['status'],'stage':x['current_stage_order'],'created_at':x['created_at'],'completed_at':x['completed_at']} for x in attempts],
                         'tasks':tasks,'native_source_preserved':True}
    if record['kind']=='change' and not meta['old_values_available']:
        proposed=meta.get('original_payload')
        record['diff']=[{'field':k,'old':'Not recorded in the historical source','new':v} for row in (proposed or []) for k,v in row.items() if k not in ['internal_record_id','edit_action']]
    if record.get('state')=='APPROVED' and mapping['target_table'] in ['g2p_register_households','g2p_register_individuals']:
        cur.execute(sql.SQL('SELECT functional_record_id FROM {} WHERE internal_record_id=%s').format(sql.Identifier(mapping['target_table'])),(mapping['target_id'],))
        target=cur.fetchone()
        if target:record['household_id']=target['functional_record_id']
    return record


def set_native_owner(cur):cur.execute("SELECT set_config('g2p.mbr_writer','on',true)")


def current_target(cur,record):
    mapping=mapped(cur,record['id'])
    cur.execute(sql.SQL('SELECT * FROM {} WHERE internal_record_id=%s FOR UPDATE').format(sql.Identifier(mapping['target_table'])),(mapping['target_id'],))
    row=cur.fetchone()
    if not row:abort(409,'Native target is unavailable.')
    data=json.loads(canonical(dict(row)));return data,digest(data)


def validate_change(cur,record,payload):
    mapping=mapped(cur,record['id']);original=mapping['metadata']['original_payload']
    proposal=payload.get('legacy_change_values') if isinstance(payload,dict) else None
    if not isinstance(proposal,list) or len(proposal)!=1 or not isinstance(original,list) or len(original)!=1:
        abort(422,'A migrated change must retain its original native record shape.')
    if set(proposal[0])!=set(original[0]):abort(422,'A migrated change may edit only its original fields.')
    for key in ['internal_record_id','edit_action']:
        if proposal[0].get(key)!=original[0].get(key):abort(422,'Native change target and action are immutable.')


def validate_preserved(cur,record):
    mapping=mapped(cur,record['id'])
    if record['kind']=='change':validate_change(cur,record,record['payload'])
    elif record['payload'].get('legacy_sections')!=mapping['metadata']['native_sections']:
        abort(409,'Preserved native sections changed. Correct and resubmit using the intake form.')


def mirror_state(cur,record,actor,at):
    mapping=mapped(cur,record['id'])
    if not mapping:return
    set_native_owner(cur)
    approval={'DRAFT':'PENDING','RETURNED':'PENDING'}.get(record['state'],record['state'])
    table='g2p_intake_form_submissions' if mapping['native_kind']=='intake' else 'g2p_register_change_requests'
    key='submission_id' if mapping['native_kind']=='intake' else 'change_request_id'
    summary=record['state'].lower()+'-stage'+str(record['stage'])
    fields={'approval_status':approval,'awe_request_status_summary':summary,'remarks':record.get('reason')}
    if record['state'] in ['APPROVED','REJECTED']:
        fields.update(approved_by=actor,approved_at=at)
    if mapping['native_kind']=='intake':
        fields.update(draft_status='DRAFT' if record['state'] in ['DRAFT','RETURNED'] else 'FINAL',last_updated_at=at)
        if record['state']=='APPROVED':fields.update(register_ingest_process_status='PROCESSED',register_ingest_processed_timestamp=at)
    cur.execute(sql.SQL('UPDATE {} SET {} WHERE {}=%s').format(sql.Identifier(table),sql.SQL(',').join(sql.SQL('{}=%s').format(sql.Identifier(k)) for k in fields),sql.Identifier(key)),[*fields.values(),mapping['native_key']])
    cur.execute(sql.SQL('SELECT * FROM {} WHERE {}=%s').format(sql.Identifier(table),sql.Identifier(key)),(mapping['native_key'],))
    current=json.loads(canonical(dict(cur.fetchone())))
    cur.execute("UPDATE g2p_mbr_native_map SET metadata=jsonb_set(jsonb_set(metadata,'{native_current}',%s),'{assignment_released}','true'::jsonb) WHERE submission_id=%s",(Json(current),str(record['id'])))


def columns(cur,table):
    cur.execute('SELECT column_name FROM information_schema.columns WHERE table_schema=current_schema() AND table_name=%s',(table,))
    return {x['column_name'] for x in cur.fetchall()}


def history(cur,table,row,record,mapping,actor,at):
    htable=table.replace('g2p_register_','g2p_register_history_',1);allowed=columns(cur,htable)
    if not allowed:return
    values={k:v for k,v in row.items() if k in allowed}
    original=mapping['metadata']['original']
    values.update({k:v for k,v in {'history_record_id':str(uuid.uuid4()),'internal_record_id':row['internal_record_id'],
                  'subject_internal_record_id':mapping['target_id'],'submission_id':mapping['native_key'] if record['kind']=='intake' else None,
                  'change_request_id':mapping['native_key'] if record['kind']=='change' else None,'created_by':record['created_by'],
                  'created_at':record['created_at'],'approved_by':actor,'approved_at':at,'is_primary_section':True,
                  'change_request_source':'MBR_WORKFLOW','tab_id':original.get('tab_id'),'section_id':original.get('section_id')}.items() if k in allowed})
    insert(cur,htable,values)


def insert(cur,table,values):
    cur.execute(sql.SQL('INSERT INTO {} ({}) VALUES ({})').format(sql.Identifier(table),sql.SQL(',').join(map(sql.Identifier,values)),
                sql.SQL(',').join(sql.Placeholder() for _ in values)),[Json(v) if isinstance(v,(dict,list)) else v for v in values.values()])


def publish(cur,record,actor,at):
    """Apply the preserved native schema, without silently inventing new survey attributes."""
    mapping=mapped(cur,record['id'])
    if not mapping:raise ValueError('Missing native migration mapping')
    meta=mapping['metadata'];set_native_owner(cur)
    if record['kind']=='change':
        table=mapping['target_table']
        cur.execute(sql.SQL('SELECT * FROM {} WHERE internal_record_id=%s FOR UPDATE').format(sql.Identifier(table)),(mapping['target_id'],))
        current=cur.fetchone()
        if not current:abort(409,'Native change target no longer exists.')
        if record.get('base_revision') and digest(json.loads(canonical(dict(current))))!=record['base_revision']:
            abort(409,'The native record changed during review. Return this request for correction.')
        proposed=record['payload'].get('legacy_change_values')
        if not isinstance(proposed,list) or len(proposed)!=1:abort(422,'This legacy change needs one native record payload.')
        allowed=columns(cur,table)-{'internal_record_id','functional_record_id','created_by','created_at','last_approved_by','last_approved_at'}
        values={k:v for k,v in proposed[0].items() if k in allowed}
        if not values:abort(422,'No supported native fields were changed.')
        values.update(last_approved_by=actor,last_approved_at=at)
        cur.execute(sql.SQL('UPDATE {} SET {} WHERE internal_record_id=%s RETURNING *').format(sql.Identifier(table),sql.SQL(',').join(sql.SQL('{}=%s').format(sql.Identifier(k)) for k in values)),
                    [*[Json(v) if isinstance(v,(dict,list)) else v for v in values.values()],mapping['target_id']])
        history(cur,table,dict(cur.fetchone()),record,mapping,actor,at)
        return mapping['target_id']
    sections=record['payload'].get('legacy_sections')
    if not sections:abort(422,'The native intake has no preserved section records. Return it for correction.')
    for source,records in sections.items():
        table=source.replace('g2p_intake_form_','g2p_register_',1);allowed=columns(cur,table)
        if not allowed:abort(422,'A native intake section has no matching master schema.')
        for row in records:
            values={k:v for k,v in row.items() if k in allowed}
            if not values.get('internal_record_id'):abort(422,'Native record identifier is missing.')
            cur.execute(sql.SQL('SELECT 1 FROM {} WHERE internal_record_id=%s FOR UPDATE').format(sql.Identifier(table)),(values['internal_record_id'],))
            if cur.fetchone():abort(409,'A native master record already exists for this intake. Resolve this conflict before approving.')
            if table=='g2p_register_households' and not values.get('functional_record_id'):
                cur.execute('SELECT pg_advisory_xact_lock(73291408)')
                while True:
                    value='HH-'+str(uuid.uuid4().int%10000000000).zfill(10)
                    cur.execute('SELECT 1 FROM g2p_register_households WHERE functional_record_id=%s',(value,))
                    if not cur.fetchone():break
                values['functional_record_id']=value
            values.update(record_status='ACTIVE',last_approved_at=at,last_approved_by=actor)
            insert(cur,table,values);history(cur,table,values,record,mapping,actor,at)
    return mapping['target_id']


def install(r):
    with r.pg('register') as c:
        with c.cursor() as cur:cur.execute(DDL)
    @r.app.get(r.PREFIX+'/mbr/legacy')
    def mbr_native_route():
        path=request.args.get('path','')
        from urllib.parse import urlencode
        if not path.startswith(('/en/','/en','/')) or len(path)>500:abort(400)
        view='tasks' if '/tasks' in path or path.startswith('/awe/') else 'changes' if '/change-request' in path else 'submissions' if '/intake-form' in path else 'dashboard'
        candidate=path.rstrip('/').split('/')[-1]
        query={'view':view,'status':'All'}
        if view!='dashboard':
            with r.pg('register') as c:
                with c.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute('''SELECT submission_id FROM g2p_mbr_native_map m WHERE native_key=%s OR request_id=%s OR metadata->'attempt_ids' ? %s
                     OR EXISTS(SELECT 1 FROM g2p_mbr_source_archive a WHERE a.source_db='awe' AND a.source_table='approval_task' AND a.body->>'id'=%s AND m.metadata->'attempt_ids' ? (a.body->>'request_id'))''',(candidate,candidate,candidate,candidate))
                    row=cur.fetchone()
                    if row:query['id']=str(row['submission_id'])
                    elif path.startswith('/awe/'):
                        return redirect('https://g2p-awe.wverve.in'+path[4:]+'?native_view=1')
        return redirect(r.PREFIX+'/mbr?'+urlencode(query))
