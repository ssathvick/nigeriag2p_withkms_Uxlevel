"""Two-stage MBR workspace. Workflow and native master changes share one PG transaction."""
import datetime as dt
import hashlib
import json
import re
import secrets
import uuid
from collections import Counter
from difflib import SequenceMatcher

from flask import abort, g, request
from psycopg2.extras import Json, RealDictCursor
import mbr_native_bridge as native_bridge

ROLES = {'mbr-officer': 'Registration Officer', 'mbr-field-agent': 'Field Agent',
         'mbr-level1': 'Level 1 Approver', 'mbr-level2': 'Level 2 Approver', 'mbr-admin': 'Administrator'}
SPONSORS = ['NG CARES', 'UNICEF', 'GIZ', 'STATE SPONSORED', 'WORLD FOOD PROGRAMME', 'Others']
SHOCKS = ['Flood', 'Drought', 'Conflict/Violence', 'Epidemic', 'Storm', 'Fire']
CROPS = ['Beans', 'Cassava', 'Kolanut', 'Maize', 'Millet', 'Oil Palm']
ASSETS = ['Radio', 'TV', 'Generator', 'Mobile Phone', 'Torch', 'Stove', 'Landline', 'House', 'Land',
          'Refrigerator', 'Freezer', 'Furniture', 'Hi-Fi', 'Mattress', 'Bed', 'Computer', 'Washing Machine']
RELATIONS = ['Head of Household', 'Spouse', 'Child', 'Parent', 'Sibling', 'Grandchild', 'Other relative', 'Other']
SCHEMA = '''
CREATE TABLE IF NOT EXISTS g2p_mbr_submissions (
 id UUID PRIMARY KEY, reference TEXT UNIQUE NOT NULL, kind TEXT NOT NULL CHECK(kind IN ('intake','change')),
 state TEXT NOT NULL CHECK(state IN ('DRAFT','RETURNED','PENDING','REJECTED','APPROVED')),
 stage INTEGER NOT NULL DEFAULT 1 CHECK(stage IN (1,2)), version INTEGER NOT NULL DEFAULT 1,
 payload JSONB NOT NULL, old_payload JSONB, master_id TEXT, base_revision TEXT,
 source TEXT NOT NULL, created_by TEXT NOT NULL, created_name TEXT NOT NULL,
 created_at TIMESTAMPTZ NOT NULL DEFAULT now(), updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
 reason TEXT, level1_actor TEXT, client_id TEXT, UNIQUE(created_by,client_id));
CREATE UNIQUE INDEX IF NOT EXISTS g2p_mbr_open_change ON g2p_mbr_submissions(master_id)
 WHERE kind='change' AND state IN ('DRAFT','RETURNED','PENDING');
CREATE TABLE IF NOT EXISTS g2p_mbr_master_data (
 native_id TEXT PRIMARY KEY, payload JSONB NOT NULL, updated_at TIMESTAMPTZ NOT NULL DEFAULT now());
CREATE TABLE IF NOT EXISTS g2p_mbr_events (
 id BIGSERIAL PRIMARY KEY, submission_id UUID NOT NULL REFERENCES g2p_mbr_submissions(id),
 actor TEXT NOT NULL, action TEXT NOT NULL, comment TEXT NOT NULL DEFAULT '', at TIMESTAMPTZ NOT NULL DEFAULT now());
ALTER TABLE g2p_mbr_events ADD COLUMN IF NOT EXISTS actor_name TEXT;
'''


def full_name(m):
    return ' '.join(str(m.get(k) or '').strip() for k in ('first_name', 'other_name', 'surname') if m.get(k))


def head(p):
    return next((m for m in p.get('members', []) if m.get('relationship') == 'Head of Household'), {})


def fingerprint(p):
    return hashlib.sha256(json.dumps(p, sort_keys=True, default=str).encode()).hexdigest()


def validate(p, final=False):
    if not isinstance(p, dict):
        abort(422, 'Household data must be an object.')
    if len(json.dumps(p)) > 48000:
        abort(422, 'Household data exceeds the supported size.')
    if not isinstance(p.get('members', []), list) or len(p.get('members', [])) > 100:
        abort(422, 'A household may contain up to 100 members.')
    if not final:
        return
    errors = []
    def need(test, message):
        if not test: errors.append(message)
    need(p.get('consent') == 'Yes', 'Survey consent is required before submission.')
    need(p.get('sponsor') in SPONSORS, 'Select a survey sponsor.')
    for key in ['enumerator', 'state', 'zone', 'community', 'serial_number', 'address']:
        need(bool(str(p.get(key) or '').strip()), key.replace('_', ' ').capitalize() + ' is required.')
    members = p.get('members', [])
    need(bool(members), 'Add at least one household member.')
    need(p.get('complete_members') == 'Yes', 'Confirm that the member list is complete.')
    heads = sum(m.get('relationship') == 'Head of Household' for m in members if isinstance(m, dict))
    try: need(int(p.get('number_heads', 0)) == heads and heads > 0, 'Number of heads must match the member list.')
    except (ValueError, TypeError): need(False, 'Enter a valid number of household heads.')
    ids = set()
    nins = set()
    today = dt.datetime.now(dt.timezone(dt.timedelta(hours=5, minutes=30))).date()
    for i, m in enumerate(members):
        if not isinstance(m, dict): abort(422, 'Invalid household member.')
        label = f'Member {i + 1}: '
        need(bool(m.get('first_name')) and bool(m.get('surname')), label + 'first name and surname are required.')
        need(m.get('relationship') in RELATIONS, label + 'select a relationship.')
        need(m.get('sex') in ['Male', 'Female', 'Other'], label + 'select sex.')
        mid = m.get('id')
        need(isinstance(mid, str) and bool(re.fullmatch(r'[a-zA-Z0-9-]{1,80}', mid or '')) and mid not in ids, label + 'member identifier is invalid or repeated.')
        ids.add(mid)
        try:
            age = int(m.get('age', -1)); need(0 <= age <= 120, label + 'age must be between 0 and 120.')
            if m.get('dob'):
                dob = dt.date.fromisoformat(m['dob'])
                actual = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
                need(dob <= today and abs(actual - age) <= 1, label + 'date of birth and age must agree.')
        except (ValueError, TypeError): need(False, label + 'enter a valid age and date of birth.')
        need(m.get('valid_nin') in ['Yes', 'No'], label + 'choose whether a valid NIN is available.')
        if m.get('valid_nin') == 'Yes':
            nin = str(m.get('nin', ''))
            need(bool(re.fullmatch(r'\d{11}', nin)), label + 'NIN must contain 11 digits.')
            need(nin not in nins, label + 'NIN is repeated within this household.'); nins.add(nin)
        else:
            need(bool(str(m.get('tracking_number') or '').strip()), label + 'enter a NIN tracking number.')
            need(m.get('tracking_confirmed') == 'Yes', label + 'confirm the tracking number.')
        for key, length in [('bank_account', 10), ('bvn', 11)]:
            need(not m.get(key) or bool(re.fullmatch(r'\d{' + str(length) + '}', str(m[key]))), label + key.replace('_', ' ') + f' must contain {length} digits.')
        need(not m.get('phone') or bool(re.fullmatch(r'\+?[0-9 ()-]{7,20}', str(m['phone']))), label + 'enter a valid phone number.')
    for key, low, high in [('latitude', -90, 90), ('longitude', -180, 180)]:
        if p.get(key) not in ('', None):
            try: need(low <= float(p[key]) <= high, key.capitalize() + ' is outside its valid range.')
            except (ValueError, TypeError): need(False, key.capitalize() + ' must be numeric.')
    for key in ['roof', 'floor', 'water', 'lighting', 'cooking_fuel', 'income_source']:
        need(bool(p.get(key)), 'Complete ' + key.replace('_', ' ') + '.')
    for key in ['health_insurance', 'grows_crops']:
        need(p.get(key) in ['Yes', 'No'], 'Complete ' + key.replace('_', ' ') + '.')
    try: need(int(p.get('rooms', 0)) > 0, 'Rooms must be a positive whole number.')
    except (ValueError, TypeError): need(False, 'Enter a valid number of rooms.')
    try: need(float(p.get('monthly_income', 0)) >= 0, 'Income cannot be negative.')
    except (ValueError, TypeError): need(False, 'Enter valid monthly income.')
    for key, allowed in [('shocks', SHOCKS), ('crops', CROPS)]:
        values = p.get(key, [])
        need(isinstance(values, list) and all(v in allowed for v in values), 'Invalid ' + key + '.')
    need(p.get('grows_crops') != 'Yes' or bool(p.get('crops')), 'Select crops grown.')
    if p.get('shocks'):
        try: need(today.year - 3 <= int(p.get('shock_year', 0)) <= today.year, 'Shock year must fall within the past three years.')
        except (ValueError, TypeError): need(False, 'Enter a valid shock year.')
    assets = p.get('assets', {})
    need(isinstance(assets, dict), 'Invalid asset information.')
    if isinstance(assets, dict):
        for asset in ASSETS:
            need(assets.get(asset) in ['Yes', 'No'], 'Complete asset ownership: ' + asset + '.')
        for asset in ['TV', 'Generator']:
            if assets.get(asset) == 'Yes':
                try: need(int(p.get(asset.lower() + '_count', 0)) > 0, asset + ' count must be positive.')
                except (ValueError, TypeError): need(False, 'Enter a valid ' + asset + ' count.')
    if errors: abort(422, '\n'.join(errors))


def compare(candidate, match):
    a, b = head(candidate), head(match)
    an, bn = full_name(a) or candidate.get('household_head_name') or '', full_name(b) or match.get('household_head_name') or ''
    name_score = round(SequenceMatcher(None, an.casefold(), bn.casefold()).ratio() * 100) if an and bn else 0
    try: age_score = max(0, 100 - abs(int(a['age']) - int(b['age'])) * 10)
    except (ValueError, KeyError, TypeError): age_score = 0
    sex_score = 100 if a.get('sex') and a.get('sex') == b.get('sex') else 0
    exact_nin = bool(set(str(m['nin']) for m in candidate.get('members', []) if m.get('valid_nin') == 'Yes' and m.get('nin')) &
                     set(str(m['nin']) for m in match.get('members', []) if m.get('valid_nin') == 'Yes' and m.get('nin')))
    score = 100 if exact_nin else round(name_score * .65 + age_score * .2 + sex_score * .15)
    return {'score': score, 'exact_nin': exact_nin, 'name_score': name_score, 'age_score': age_score,
            'sex_score': sex_score, 'fields': [
                {'field': 'Head of household', 'candidate': an, 'match': bn},
                {'field': 'Age', 'candidate': a.get('age'), 'match': b.get('age')},
                {'field': 'Sex', 'candidate': a.get('sex'), 'match': b.get('sex')},
                {'field': 'NIN', 'candidate': '•••••••' + str(a.get('nin', ''))[-4:] if a.get('nin') else 'Not available',
                 'match': '•••••••' + str(b.get('nin', ''))[-4:] if b.get('nin') else 'Not available'}]}


def diff(old, new, path=''):
    result = []
    if isinstance(old, dict) and isinstance(new, dict):
        for key in sorted(set(old) | set(new)):
            result.extend(diff(old.get(key), new.get(key), (path + '.' if path else '') + key))
    elif old != new:
        result.append({'field': path, 'old': old, 'new': new})
    return result


def install(r):
    app = r.app
    prefix = r.PREFIX + '/mbr'
    with r.pg('register') as c:
        with c.cursor() as cur: cur.execute(SCHEMA)
    native_bridge.install(r)

    def identity():
        r.require_user()
        assigned = set(g.user.get('roles', [])) & set(ROLES)
        if g.session.get('mode') != 'staff' or len(assigned) != 1:
            abort(403, 'An assigned MBR staff role is required. Contact your administrator.')
        return next(iter(assigned)), g.user['sub']

    def require(*roles):
        role, actor = identity()
        if role not in roles: abort(403, 'Your role cannot perform this action.')
        return role, actor

    def load_master(cur, master_id=None, lock=False):
        query = 'SELECT * FROM g2p_register_households'
        args = ()
        if master_id:
            query += ' WHERE internal_record_id=%s'; args = (master_id,)
        else: query += " WHERE record_status='ACTIVE'"
        query += ' ORDER BY created_at DESC'
        if lock: query += ' FOR UPDATE'
        cur.execute(query, args); households = [dict(x) for x in cur.fetchall()]
        if not households: return []
        ids = [x['internal_record_id'] for x in households]
        cur.execute("SELECT * FROM g2p_register_individuals WHERE link_internal_record_id=ANY(%s) AND record_status='ACTIVE' ORDER BY internal_record_id", (ids,))
        people = [dict(x) for x in cur.fetchall()]
        cur.execute('SELECT * FROM g2p_mbr_master_data WHERE native_id=ANY(%s)', (ids,))
        extras = {x['native_id']: x['payload'] for x in cur.fetchall()}
        result = []
        for h in households:
            p = dict(extras.get(h['internal_record_id'], {}))
            # Read current native demographic values so edits through other interfaces invalidate a pending CR.
            old_members = {m['id']: m for m in p.get('members', [])}
            members = []
            for m in people:
                if m['link_internal_record_id'] != h['internal_record_id']: continue
                v = dict(old_members.get(m['internal_record_id'], {}))
                v.update(id=m['internal_record_id'], first_name=m.get('first_name') or m.get('given_name') or '',
                         surname=m.get('last_name') or '', other_name=m.get('middle_name') or '',
                         relationship='Head of Household' if m['internal_record_id'] == h.get('household_head_internal_record_id') else m.get('relationship_to_head') or v.get('relationship', 'Other'),
                         sex=str(m.get('gender') or '').title(), dob=str(m['birth_date']) if m.get('birth_date') else '',
                         age=m.get('estimated_age') if m.get('estimated_age') is not None else v.get('age', ''),
                         nin=m.get('foundational_id') or v.get('nin', ''), education=m.get('education_level') or v.get('education', ''))
                if v['dob']:
                    born = dt.date.fromisoformat(v['dob']); today = dt.date.today()
                    v['age'] = today.year - born.year - ((today.month, today.day) < (born.month, born.day))
                v.setdefault('valid_nin', 'Yes' if re.fullmatch(r'\d{11}', str(v['nin'])) else 'No')
                members.append(v)
            p.update(members=members, community=p.get('community') or '',
                     address=h.get('address_line_1') or p.get('address', ''), latitude=h.get('latitude'), longitude=h.get('longitude'))
            result.append({'id': h['internal_record_id'], 'household_id': h['functional_record_id'],
                           'title': h.get('household_head_name') or h.get('record_name') or 'Household',
                           'state': 'APPROVED', 'record_status': h['record_status'], 'payload': p,
                           'revision': fingerprint({'payload': p, 'native_updated': str(h['last_approved_at'])}),
                           'created_at': h['created_at'], 'kind': 'master'})
        return result

    def submission(cur, sid, lock=False):
        try: uuid.UUID(sid)
        except (ValueError, TypeError): abort(404, 'Submission not found.')
        cur.execute('SELECT * FROM g2p_mbr_submissions WHERE id=%s' + (' FOR UPDATE' if lock else ''), (sid,))
        s = cur.fetchone()
        if not s: abort(404, 'Submission not found.')
        s = dict(s); role, actor = identity()
        if role in ('mbr-officer', 'mbr-field-agent') and s['created_by'] not in native_bridge.actor_ids(cur,g.user):
            abort(403, 'This submission belongs to another officer.')
        return s

    def event(cur, sid, action, comment=''):
        cur.execute('INSERT INTO g2p_mbr_events(submission_id,actor,actor_name,action,comment) VALUES(%s,%s,%s,%s,%s)',
                    (str(sid), g.user['sub'], g.user.get('name') or g.user.get('email') or 'Assigned reviewer', action, comment))

    def publish(cur, s, actor):
        if s.get('native_origin')=='native':
            return native_bridge.publish(cur,s,actor,r.stamp())
        p = s['payload']; validate(p, True)
        hid = s.get('master_id') or str(uuid.uuid4())
        if s['kind'] == 'change':
            masters = load_master(cur, hid, True)
            if not masters or masters[0]['revision'] != s['base_revision']:
                abort(409, 'The master record changed during review. Return this request for correction and refresh its baseline.')
            functional_id = masters[0]['household_id']
        else:
            # Lock allocation across workers. Preserve all legacy IDs, allocate numeric ten-digit IDs for new households.
            cur.execute('SELECT pg_advisory_xact_lock(73291408)')
            while True:
                functional_id = 'HH-' + ''.join(secrets.choice('0123456789') for _ in range(10))
                cur.execute('SELECT 1 FROM g2p_register_households WHERE functional_record_id=%s', (functional_id,))
                if not cur.fetchone(): break
        now = r.stamp(); h = head(p)
        values = {'internal_record_id': hid, 'functional_record_id': functional_id, 'record_name': full_name(h),
                  'created_by': s['created_by'], 'created_at': now, 'last_approved_at': now, 'last_approved_by': actor,
                  'record_status': 'ACTIVE', 'search_text': full_name(h) + ' ' + functional_id,
                  'household_head_internal_record_id': h['id'], 'household_head_name': full_name(h),
                  'size_total': len(p['members']), 'size_adults': sum(int(m['age']) >= 18 for m in p['members']),
                  'country_code': 'NGA', 'address_line_1': p['address'], 'latitude': p.get('latitude') or None,
                  'longitude': p.get('longitude') or None, 'roof_material': p['roof'], 'floor_material': p['floor'],
                  'rooms_count': int(p['rooms']), 'water_source_type': p['water'], 'lighting_source': p['lighting'],
                  'cooking_fuel_type': p['cooking_fuel']}
        def upsert(table, data, preserve=()):
            keys = list(data)
            from psycopg2 import sql
            updates = [k for k in keys if k not in ('internal_record_id', *preserve)]
            cur.execute(sql.SQL('INSERT INTO {} ({}) VALUES ({}) ON CONFLICT(internal_record_id) DO UPDATE SET {}').format(
                sql.Identifier(table), sql.SQL(',').join(map(sql.Identifier, keys)), sql.SQL(',').join(sql.Placeholder() for _ in keys),
                sql.SQL(',').join(sql.SQL('{}=EXCLUDED.{}').format(sql.Identifier(k), sql.Identifier(k)) for k in updates)), list(data.values()))
        upsert('g2p_register_households', values, ('created_by', 'created_at'))
        mids = [m['id'] for m in p['members']]
        # Member IDs supplied by the client may never reparent another household's members.
        cur.execute('SELECT internal_record_id FROM g2p_register_individuals WHERE internal_record_id=ANY(%s) AND (link_internal_record_id IS DISTINCT FROM %s)', (mids, hid))
        if cur.fetchone(): abort(409, 'A member identifier belongs to another household.')
        for m in p['members']:
            iv = {'internal_record_id': m['id'], 'functional_record_id': 'IN-' + uuid.uuid5(uuid.NAMESPACE_URL, hid + '/' + m['id']).hex[:14].upper(),
                  'link_internal_record_id': hid, 'record_name': full_name(m), 'full_name': full_name(m),
                  'created_by': s['created_by'], 'created_at': now, 'last_approved_at': now, 'last_approved_by': actor,
                  'record_status': 'ACTIVE', 'search_text': full_name(m), 'first_name': m['first_name'], 'given_name': m['first_name'],
                  'last_name': m['surname'], 'middle_name': m.get('other_name', ''), 'gender': m['sex'],
                  'birth_date': m.get('dob') or None, 'estimated_age': int(m['age']), 'relationship_to_head': m['relationship'],
                  'foundational_id': m.get('nin') if m.get('valid_nin') == 'Yes' else None,
                  'marital_status': m.get('marital_status'), 'education_level': m.get('education'), 'country_code': 'NGA',
                  'address_line_1': p['address']}
            upsert('g2p_register_individuals', iv, ('created_by', 'created_at', 'functional_record_id'))
        cur.execute("UPDATE g2p_register_individuals SET record_status='INACTIVE',last_approved_at=%s,last_approved_by=%s WHERE link_internal_record_id=%s AND NOT(internal_record_id=ANY(%s))", (now, actor, hid, mids))
        cur.execute('INSERT INTO g2p_mbr_master_data(native_id,payload) VALUES(%s,%s) ON CONFLICT(native_id) DO UPDATE SET payload=EXCLUDED.payload,updated_at=now()', (hid, Json(p)))
        return hid

    @app.get(prefix)
    @app.get(prefix + '/')
    def mbr_home():
        if not g.user:
            g.session['mbr_return']=request.full_path.rstrip('?')
            return r.redirect(r.PREFIX + '/login?mode=staff&mbr=1')
        role, actor = identity()
        return r.page('mbr.html', mbr_role=role, mbr_role_name=ROLES[role])

    @app.get(prefix + '/api/bootstrap')
    def mbr_bootstrap():
        role, actor = identity()
        with r.pg('register') as c:
            with c.cursor(cursor_factory=RealDictCursor) as cur:
                masters = load_master(cur)
                clause = ' WHERE created_by=ANY(%s)' if role in ('mbr-officer', 'mbr-field-agent') else ''
                cur.execute('SELECT * FROM g2p_mbr_submissions' + clause + ' ORDER BY created_at DESC', (native_bridge.actor_ids(cur,g.user),) if clause else ())
                submissions = [dict(s) for s in cur.fetchall()]
                for s in submissions:s['assigned_to_me']=native_bridge.assigned(cur,s,g.user)
        return {'role': role, 'actor': actor, 'role_name': ROLES[role], 'user': g.user.get('name') or g.user.get('email'),
                'submissions': submissions, 'masters': masters,
                'configuration': {'sponsors': SPONSORS, 'shocks': SHOCKS, 'crops': CROPS, 'assets': ASSETS,
                                  'roles': ROLES, 'workflow': ['DRAFT', 'PENDING (Stage 1)', 'PENDING (Stage 2)', 'APPROVED / ACTIVE']}}

    @app.get(prefix + '/api/submissions/<sid>')
    def mbr_detail(sid):
        identity()
        with r.pg('register') as c:
            with c.cursor(cursor_factory=RealDictCursor) as cur:
                s = submission(cur, sid)
                s['assigned_to_me']=native_bridge.assigned(cur,s,g.user)
                cur.execute("SELECT coalesce(actor_name,'Assigned reviewer') AS actor,action,comment,at FROM g2p_mbr_events WHERE submission_id=%s ORDER BY at,id", (sid,))
                s['events'] = [dict(x) for x in cur.fetchall()]
                if s['state'] == 'APPROVED' and s['master_id']:
                    cur.execute('SELECT functional_record_id FROM g2p_register_households WHERE internal_record_id=%s', (s['master_id'],))
                    master = cur.fetchone()
                    s['household_id'] = master['functional_record_id'] if master else None
                cur.execute("SELECT id,reference,payload FROM g2p_mbr_submissions WHERE id<>%s AND state='PENDING' AND kind='intake'", (sid,))
                intake = [{'id': str(x['id']), 'reference': x['reference'], **compare(s['payload'], x['payload'])} for x in cur.fetchall()]
                existing = [{'id': x['id'], 'reference': x['household_id'], **compare(s['payload'], x['payload'])}
                            for x in load_master(cur) if x['id'] != s['master_id']]
                s['duplicates'] = {k: sorted([v for v in vals if v['score'] >= 65], key=lambda x: -x['score']) for k, vals in [('intake', intake), ('existing', existing)]}
                s['diff'] = diff(s.get('old_payload') or {}, s['payload']) if s['kind'] == 'change' else []
                return native_bridge.enrich(cur,s)

    def body():
        try: data = json.loads(request.form.get('payload', '{}'))
        except (ValueError, TypeError): abort(400, 'Invalid request payload.')
        if not isinstance(data, dict): abort(400, 'Invalid request payload.')
        return data

    def create(cur, data, actor, role):
        p = data.get('data', {}); final = data.get('submit') is True
        validate(p, final)
        kind = data.get('kind', 'intake')
        if kind not in ['intake', 'change']: abort(422, 'Invalid submission kind.')
        master_id = data.get('master_id'); old = None; revision = None
        if kind == 'change':
            if role != 'mbr-officer': abort(403, 'Only registration officers may request master changes.')
            masters = load_master(cur, master_id, True) if master_id else []
            if not masters: abort(404, 'Master household not found.')
            old = masters[0]['payload']; revision = masters[0]['revision']
            if data.get('base_revision') != revision: abort(409, 'Master record changed. Reopen Edit Details before saving.')
            if not diff(old, p): abort(422, 'Change at least one field before saving a change request.')
            cur.execute("SELECT 1 FROM g2p_mbr_submissions WHERE master_id=%s AND state IN ('DRAFT','RETURNED','PENDING')", (master_id,))
            if cur.fetchone(): abort(409, 'This household already has an open change request.')
        else: master_id = None
        client_id = data.get('client_id')
        if client_id:
            if not isinstance(client_id, str) or len(client_id) > 100: abort(422, 'Invalid sync identifier.')
            cur.execute('SELECT * FROM g2p_mbr_submissions WHERE created_by=%s AND client_id=%s', (actor, client_id))
            prior = cur.fetchone()
            if prior:
                if prior['payload'] != p: abort(409, 'This sync identifier was already used for different data.')
                return dict(prior)
        sid = str(uuid.uuid4()); day = dt.datetime.now(dt.timezone(dt.timedelta(hours=5, minutes=30)))
        # A UUID-derived six digit reference is collision-checked and retried under an allocation lock.
        cur.execute('SELECT pg_advisory_xact_lock(73291409)')
        while True:
            reference = day.strftime('%Y%b%d').upper() + '-' + f'{secrets.randbelow(1000000):06d}'
            cur.execute('SELECT 1 FROM g2p_mbr_submissions WHERE reference=%s', (reference,))
            if not cur.fetchone(): break
        source = 'Offline Data Collection' if role == 'mbr-field-agent' else 'Staff Portal'
        cur.execute('''INSERT INTO g2p_mbr_submissions(id,reference,kind,state,payload,old_payload,master_id,base_revision,source,created_by,created_name,client_id)
         VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING *''',
                    (sid, reference, kind, 'PENDING' if final else 'DRAFT', Json(p), Json(old) if old else None, master_id, revision, source,
                     actor, g.user.get('name') or g.user.get('email') or actor, client_id))
        result = dict(cur.fetchone()); event(cur, sid, 'submitted' if final else 'draft_saved'); return result

    @app.post(prefix + '/api/submissions')
    def mbr_create():
        role, actor = require('mbr-officer', 'mbr-field-agent'); data = body()
        with r.pg('register') as c:
            with c.cursor(cursor_factory=RealDictCursor) as cur: result = create(cur, data, actor, role)
        return result, 201

    @app.post(prefix + '/api/sync')
    def mbr_sync():
        role, actor = require('mbr-field-agent'); data = body(); batch = data.get('batch')
        if not isinstance(batch, list) or not 1 <= len(batch) <= 10: abort(422, 'Sync between one and ten households at a time.')
        if any(not isinstance(x, dict) or not x.get('client_id') for x in batch): abort(422, 'Each household needs a sync identifier.')
        with r.pg('register') as c:
            with c.cursor(cursor_factory=RealDictCursor) as cur:
                # Atomic and idempotent: one invalid record rolls back the entire batch.
                cur.execute('SELECT pg_advisory_xact_lock(73291410)')
                result = [create(cur, {**x, 'submit': True, 'kind': 'intake'}, actor, role) for x in batch]
        return {'synced': result}

    @app.post(prefix + '/api/submissions/<sid>/save')
    def mbr_save(sid):
        role, actor = require('mbr-officer', 'mbr-field-agent'); data = body()
        with r.pg('register') as c:
            with c.cursor(cursor_factory=RealDictCursor) as cur:
                s = submission(cur, sid, True)
                if s['created_by'] not in native_bridge.actor_ids(cur,g.user) or s['state'] not in ['DRAFT', 'RETURNED']: abort(409, 'Only your drafts and returned submissions can be edited.')
                if data.get('version') != s['version']: abort(409, 'Another session changed this record. Reload it before saving.')
                p = data.get('data', {})
                legacy_change=s.get('native_origin')=='native' and s['kind']=='change'
                if legacy_change:native_bridge.validate_change(cur,s,p)
                else:validate(p, data.get('submit') is True)
                baseline, revision = s['old_payload'], s['base_revision']
                if s['kind'] == 'change' and data.get('refresh_baseline'):
                    if legacy_change:baseline,revision=native_bridge.current_target(cur,s)
                    else:
                        masters = load_master(cur, s['master_id'], True)
                        if not masters: abort(404, 'Master household not found.')
                        baseline, revision = masters[0]['payload'], masters[0]['revision']
                cur.execute('''UPDATE g2p_mbr_submissions SET payload=%s,state=%s,stage=1,level1_actor=NULL,
                  version=version+1,updated_at=now(),old_payload=%s,base_revision=%s WHERE id=%s RETURNING *''',
                            (Json(p), 'PENDING' if data.get('submit') is True else 'DRAFT', Json(baseline) if baseline else None, revision, sid))
                result = dict(cur.fetchone())
                if s.get('native_origin')=='native' and not legacy_change:
                    cur.execute("UPDATE g2p_mbr_submissions SET native_origin='native-normalized' WHERE id=%s",(sid,));result['native_origin']='native-normalized'
                native_bridge.mirror_state(cur,result,actor,r.stamp())
                event(cur, sid, 'resubmitted' if data.get('submit') is True else 'draft_saved')
        return result

    @app.post(prefix + '/api/submissions/<sid>/decision')
    def mbr_decision(sid):
        role, actor = require('mbr-level1', 'mbr-level2'); data = body()
        action = data.get('action'); comment = str(data.get('comment') or '').strip()
        if action not in ['approve', 'return', 'reject']: abort(422, 'Invalid decision.')
        if action in ['return', 'reject'] and not comment: abort(422, 'A reason is required.')
        if len(comment) > 2000: abort(422, 'Reason must not exceed 2,000 characters.')
        with r.pg('register') as c:
            with c.cursor(cursor_factory=RealDictCursor) as cur:
                s = submission(cur, sid, True)
                if s['state'] != 'PENDING' or data.get('version') != s['version']: abort(409, 'This task has already changed. Reload before deciding.')
                expected = 'mbr-level1' if s['stage'] == 1 else 'mbr-level2'
                if role != expected: abort(403, 'This task is assigned to a different approval stage.')
                if not native_bridge.assigned(cur,s,g.user):abort(403,'This migrated task is assigned to a different reviewer.')
                aliases=native_bridge.actor_ids(cur,g.user)
                if any(x in aliases for x in [s['created_by'], s.get('level1_actor')]): abort(403, 'A different person must perform each approval stage.')
                master_id = s['master_id']; state = s['state']; stage = s['stage']; level1 = s['level1_actor']
                if action == 'approve':
                    if s.get('native_origin')=='native':native_bridge.validate_preserved(cur,s)
                    else:validate(s['payload'], True)
                    if stage == 1: stage = 2; level1 = actor
                    else: master_id = publish(cur, s, actor); state = 'APPROVED'
                else: state = 'RETURNED' if action == 'return' else 'REJECTED'
                cur.execute('''UPDATE g2p_mbr_submissions SET state=%s,stage=%s,level1_actor=%s,master_id=%s,
                  reason=%s,version=version+1,updated_at=now() WHERE id=%s RETURNING *''',
                            (state, stage, level1, master_id, comment or s['reason'], sid))
                result = dict(cur.fetchone())
                native_bridge.mirror_state(cur,result,actor,r.stamp())
                event(cur, sid, action + ('_stage1' if s['stage'] == 1 else '_stage2'), comment)
        return result

    @app.get(prefix + '/api/analytics')
    def mbr_analytics():
        require('mbr-admin')
        with r.pg('register') as c:
            with c.cursor(cursor_factory=RealDictCursor) as cur:
                masters = load_master(cur)
                cur.execute('SELECT state,count(*) AS count FROM g2p_mbr_submissions GROUP BY state')
                counts = {x['state']: x['count'] for x in cur.fetchall()}
        people = [m for h in masters for m in h['payload']['members']]
        pyramid = {band: {'Male': 0, 'Female': 0, 'Other': 0, 'Unknown': 0} for band in ['0–4', '5–17', '18–34', '35–59', '60+']}
        for m in people:
            try: age = int(m.get('age', -1))
            except (ValueError, TypeError): continue
            if age < 0: continue
            band = '0–4' if age < 5 else '5–17' if age < 18 else '18–34' if age < 35 else '35–59' if age < 60 else '60+'
            sex = m.get('sex'); pyramid[band][sex if sex in ['Male', 'Female', 'Other'] else 'Unknown'] += 1
        return {'households': len(masters), 'individuals': len(people), 'submissions': counts, 'pyramid': pyramid,
                'registration_trends': dict(Counter(str(x['created_at'])[:7] for x in masters)),
                'income_breakdown': dict(Counter(x['payload'].get('income_source') or 'Not recorded' for x in masters)),
                'nin_coverage': sum(bool(re.fullmatch(r'\d{11}', str(m.get('nin', '')))) for m in people),
                'bank_coverage': sum(bool(re.fullmatch(r'\d{10}', str(m.get('bank_account', '')))) for m in people),
                'shocks_by_year': dict(Counter(str(x['payload'].get('shock_year') or 'Not recorded') + ' · ' + shock for x in masters for shock in x['payload'].get('shocks', []))),
                'community_distribution': dict(Counter(x['payload'].get('community') or 'Not recorded' for x in masters)),
                'scope': 'Current active native Master Registry records. Missing legacy survey fields are reported as Not recorded.'}
