"""Public representative directory and strictly attributed bill evidence."""
import json,re,collections,hashlib
AS_OF='2026-11-04'
SENATE='https://naltf.gov.ng/members-of-the-senate/'
HOUSE='https://naltf.gov.ng/honorable-members/'
BILLS='https://billtracker.naltf.gov.ng/'
def norm(s):return re.sub('[^a-z0-9]','',s.lower()).replace('kastina','katsina').replace('nassarawa','nasarawa')
def person(s):
    s=re.sub(r'\b(sen|senator|hon|honourable|honorable|rt|dr|mrs|mr|reverend|prof|alhaji|chief)\b',' ',s.lower())
    return tuple(sorted(re.findall('[a-z]+',s)))

def seat_key(s):
    s=re.sub(r'\b(?:state|constituency)\b',' ',s,flags=re.I).strip()
    for roman,number in [('III','3'),('II','2'),('I','1')]:
        s=re.sub(r'\b'+roman+r'$',number,s,flags=re.I)
    return norm(s)
def add_representatives(data,raw):
    states={norm(s['name']):s for s in data['states']};states['fct']=states['federalcapitalterritory']
    districts={(d['state_id'],norm(d['name'])):d for d in data['districts']}
    reps=[];issues=[]
    for i,r in enumerate(json.loads((raw/'representative-roster-extracted.json').read_text())):
        match=re.match(r'State\s*:\s*(.*?)\s+(?:District|Constituency|Contituency)\s*:\s*(.*?)\s+Party\s*:',r['raw'],re.I)
        if not match:issues.append(r);continue
        st,seat=match.groups();state=states.get(norm(st))
        if not state:issues.append(r);continue
        chamber=r['chamber'];district=districts.get((state['id'],norm(seat))) if chamber=='Senate' else None
        rep={'id':'rep-'+hashlib.sha256((chamber+'|'+r['name']).encode()).hexdigest()[:12],'name':r['name'],'chamber':chamber,'state_id':state['id'],'state_name':state['name'],'constituency':seat,'district_id':district['id'] if district else None,'source_url':SENATE if chamber=='Senate' else HOUSE,'source_name':'National Assembly Library Trust Fund','as_of':AS_OF,'reference_year':2026,'classification':'published','level':'senatorial district' if chamber=='Senate' else 'federal constituency','status':'Listed in publisher’s 10th Assembly directory','mapping_note':'Exact normalized district name and state match to atlas codebook.' if district else 'Publisher constituency label only; no validated boundary or LGA mapping.','notes':['Directory checked on '+AS_OF+'; the publisher does not supply a row-level effective date. Changes after the snapshot may not be reflected.'],'bills':[]}
        if chamber=='Senate' and not district:rep['notes'].append('District label is incomplete or does not match the atlas codebook; no district link has been inferred.')
        reps.append(rep)
    assert not issues,issues
    for r in json.loads((raw/'ogun-members.json').read_text()):
        assert r['constituency']
        reps.append({'id':'ogun-'+r['url'].rsplit('/',1)[1],'name':r['name'],'chamber':'State House of Assembly','role':r['role'],'state_id':states['ogun']['id'],'state_name':'Ogun','constituency':r['constituency'],'district_id':None,'source_url':r['url'],'source_name':'Ogun State House of Assembly','as_of':AS_OF,'reference_year':2026,'classification':'published','level':'state constituency','status':'Listed on the assembly’s current-members page','mapping_note':'State constituency label from official member profile; no LGA or senatorial allocation inferred.','notes':['State assembly coverage currently includes Ogun only. Official member profile checked '+AS_OF+'.'],'bills':[]})
    for r in reps:
        if r['chamber']=='State House of Assembly':r['notes']=['Official member profile checked '+AS_OF+'.']
    expanded=json.loads((raw/'expanded-officials.json').read_text())
    for filename in ['lagos-officials-next.json','northern-officials-next.json','southern-officials-next.json']:
        if (raw/filename).exists():expanded.extend(json.loads((raw/filename).read_text()))
    for region in ['central','northern','southern']:
        path=raw/(region+'-round3-additions.json')
        if path.exists():expanded.extend(json.loads(path.read_text()))
    for x in expanded:
        st=states[norm(x['state'])]
        reps.append({'id':'office-'+hashlib.sha256((x['chamber']+'|'+x['state']+'|'+x['name']).encode()).hexdigest()[:12], 'name':x['name'],'chamber':x['chamber'],'role':x['role'],'state_id':st['id'],'state_name':st['name'],'constituency':x['constituency'],'district_id':None,'source_url':x['source_url'],'source_name':x['source_name'],'as_of':AS_OF,'reference_year':2026,'classification':'published','level':'state constituency' if x['chamber']=='State House of Assembly' else 'state / FCT','status':'Listed in official publisher directory; dated snapshot','mapping_note':'Publisher label only; no constituency boundary or LGA allocation inferred.','notes':[x['note'] or 'Publisher directory checked '+AS_OF+'; row-level tenure dates are not supplied.'],'bills':[]})
        for field in ['secondary_source_url','source_date','reference_year','status','corroborating_source_url','corroboration_date']:
            if x.get(field) is not None:reps[-1][field]=x[field]
        if x.get('source_date'):
            reps[-1]['reference_year']=int(x['source_date'][:4])
            reps[-1]['status']=x.get('status','Named in dated official source; later tenure changes not certified')
    assert len({r['id'] for r in reps})==len(reps),'Duplicate representative identity'
    lookup={r['id']:r for r in reps};correction_ids=set();withdrawals={}
    for region in ['central','northern','southern']:
        path=raw/(region+'-round3-corrections.json')
        for c in json.loads(path.read_text()) if path.exists() else []:
            assert c['id'] in lookup and c['id'] not in correction_ids,c
            correction_ids.add(c['id']);r=lookup[c['id']]
            assert r['chamber']=='State House of Assembly'
            if c.get('name'):assert r['name']==c['name'],(r['name'],c)
            if c.get('state'):assert r['state_name']==c['state'],(r['state_name'],c)
            r['constituency_before_review']=r['constituency']
            r['constituency']=c['constituency']
            r['constituency_evidence']={k:v for k,v in c.items() if k!='id'}
            r['constituency_evidence'].update({'classification':'published','level':'state constituency','checked_on':AS_OF,'reference_year':c.get('reference_year') or (int(c['source_date'][:4]) if c.get('source_date') else int(AS_OF[:4]))})
            r['notes'].append('Constituency reviewed against additional source: '+c['note'])
        path=raw/(region+'-round3-withdrawals.json')
        for w in json.loads(path.read_text()) if path.exists() else []:
            assert w['id'] in lookup and w['id'] not in withdrawals,w
            assert lookup[w['id']]['chamber']=='State House of Assembly'
            withdrawals[w['id']]=w
    archived=[dict(r,withdrawal=withdrawals[r['id']]) for r in reps if r['id'] in withdrawals]
    reps=[r for r in reps if r['id'] not in withdrawals]
    # Preserve conflicting publisher rows, flag them rather than choosing an occupant.
    seats=collections.Counter((r['chamber'],r['state_id'],seat_key(r['constituency'])) for r in reps if r['constituency'])
    for r in reps:
        if r['constituency'] and seats[(r['chamber'],r['state_id'],seat_key(r['constituency']))]>1:
            r['status']='Conflicting directory entries — occupant needs verification'
            r['notes'].append('Publisher lists more than one person for this constituency label. Do not infer a unique current occupant.')
    index=collections.defaultdict(list)
    for r in reps:index[(r['chamber'],person(r['name']))].append(r)
    bills=json.loads((raw/'naltf-bills.json').read_text());skips=collections.Counter();seen=set()
    for b in bills:
        if b.get('deletedAt'):skips['deleted']+=1;continue
        date=(b.get('firstReading') or '')[:10]
        if not ('2023-06-13'<=date<=AS_OF):skips['missing_or_outside_period_date']+=1;continue
        sp=b.get('sponsor') or {};chamber={'House of Reps':'House of Representatives','Senate':'Senate'}.get(sp.get('chamber'))
        if (b['number'].upper().startswith('SB') and chamber=='House of Representatives') or (b['number'].upper().startswith('HB') and chamber=='Senate'):
            skips['bill_chamber_conflict']+=1;continue
        matches=index.get((chamber,person(b.get('sponsorName') or '')),[])
        if len(matches)!=1:skips['unmatched_or_ambiguous_sponsor']+=1;continue
        r=matches[0];key=(chamber,b['number'])
        if key in seen:skips['duplicate']+=1;continue
        seen.add(key)
        r['bills'].append({'id':b['id'],'number':b['number'],'title':b['title'],'sponsor':b['sponsorName'],'first_reading':date,'second_reading':(b.get('secondReading') or '')[:10] or None,'third_reading':(b.get('thirdReading') or '')[:10] or None,'status':b['status'],'sectors':b.get('tags') or [],'source_url':BILLS+'bill/'+b['id'],'updated_at':b.get('lastUpdated'),'classification':'published','reference_year':int(date[:4]),'level':r['level']})
    for r in reps:
        for b in r['bills']:
            qualifications=[]
            for key in ['second_reading','third_reading']:
                if b[key] and not b['first_reading']<=b[key]<=AS_OF:
                    qualifications.append(key.replace('_',' ')+' date '+b[key]+' is outside the valid chronology and is excluded from date-based counts.')
                    b[key]=None
            if qualifications:b['date_qualification']=' '.join(qualifications)
        r['bills'].sort(key=lambda b:b['first_reading'],reverse=True)
    data['representatives']={'as_of':AS_OF,'period_start':'2023-06-13','period_end':AS_OF,'members':reps,'coverage':{'senate_entries':sum(r['chamber']=='Senate' for r in reps),'house_entries':sum(r['chamber']=='House of Representatives' for r in reps),'state_assembly_entries':sum(r['chamber']=='State House of Assembly' for r in reps),'districts_linked':len({r['district_id'] for r in reps if r['district_id']}),'source_bill_records':len(bills),'attributed_bill_records':len(seen),'members_with_bill_evidence':sum(bool(r['bills']) for r in reps),'conflicting_directory_entries':sum('Conflicting' in r['status'] for r in reps),'excluded_bills':dict(skips)},'methodology':['Names and seats are publisher-listed officeholders, checked on '+AS_OF+'; directory rows have no effective dates. This is a dated snapshot, not a live certified electoral register.','Senate, federal constituencies and state assembly seats are separate geographies. Only exact normalized state-and-district matches link to the existing atlas.','Bill counts are atlas aggregates of the NALTF public bill feed. Attribution requires the same chamber and exact normalized name tokens (order ignored); no fuzzy name matching or transfer from previous occupants.','Only bills with first-reading dates from 13 June 2023 to '+AS_OF+' are included. Duplicate chamber/bill-number records and bill-prefix/chamber conflicts are excluded. Missing dates, unmatched names and former members are excluded.','Stages reflect the publisher’s latest status at the snapshot, not necessarily events during the selected first-reading year. Passed does not mean presidential assent or implementation.','A bill count measures documented activity, not legislative quality, impact, attendance or personal project delivery. No composite score, league table or causal attribution of GDP/poverty is calculated.','No matched evidence is unavailable, not zero. Zero stage counts mean zero among the linked records only. Attendance needs sittings attended / eligible sittings; oversight needs committee evidence; project delivery needs verified project and implementing-agency records.'],'bill_source_url':BILLS,'bill_api_url':BILLS+'api/bills'}
    coverage=data['representatives']['coverage']
    coverage['governors']=sum(r['chamber']=='Governor' for r in reps)
    coverage['fct_ministers']=sum(r['chamber']=='FCT Minister (appointed)' for r in reps)
    coverage['assembly_states']=len({r['state_id'] for r in reps if r['chamber']=='State House of Assembly'})
    data['representatives']['state_coverage']=[{'state_id':s['id'],'name':s['name'],'assembly_entries':sum(r['state_id']==s['id'] and r['chamber']=='State House of Assembly' for r in reps),'assembly_status':'Not applicable: FCT has no State House of Assembly' if norm(s['name'])=='federalcapitalterritory' else ('Partial evidence loaded; full membership and tenure not certified' if any(r['state_id']==s['id'] and r['chamber']=='State House of Assembly' for r in reps) else 'No sufficiently verified current roster loaded; not a vacant-seat finding')} for s in data['states']]
    events=json.loads((raw/'representative-activity-evidence.json').read_text())
    for filename in ['lagos-activity-next.json','northern-activity-next.json','southern-activity-next.json']:
        if (raw/filename).exists():events.extend(json.loads((raw/filename).read_text()))
    for region in ['central','northern','southern']:
        path=raw/(region+'-round3-activity.json')
        if path.exists():events.extend(json.loads(path.read_text()))
    assert len({e['id'] for e in events})==len(events)
    for r in reps+archived:r['evidence']=sorted([{k:v for k,v in e.items() if k!='member_ids'} for e in events if r['id'] in e['member_ids']],key=lambda e:e['date'],reverse=True)
    assert all(set(e['member_ids']) <= {r['id'] for r in reps+archived} for e in events)
    coverage['activity_records']=len({e['id'] for r in reps for e in r['evidence']})
    coverage['archived_members']=len(archived)
    coverage['constituencies_reviewed']=len(correction_ids)
    coverage['assembly_seats_unverified']=sum(r['chamber']=='State House of Assembly' and not r['constituency'] for r in reps)
    for state in data['representatives']['state_coverage']:
        state['constituencies_unverified']=sum(r['chamber']=='State House of Assembly' and r['state_id']==state['state_id'] and not r['constituency'] for r in reps)
    data['representatives']['archived_members']=archived
    data['representatives']['methodology'].append('Activity records are dated official self-reports or attributed news reports with reviewed named-person attribution, not independent outcome audits. Publisher and qualifications appear on each record. Counts are documented records, not complete totals or attendance rates. Approvals and planned inspections do not establish completed projects.')
    coverage['members_with_activity_evidence']=sum(bool(r['evidence']) for r in reps)
    data['gaps'][0]=f"Governor directory covers all 36 states; FCT minister is appointed. State assembly evidence covers {coverage['assembly_states']} states, including partial rosters, dated reports and unresolved source labels. Remaining assembly members and local council heads are not verified. Boundaries and tenure dates remain incomplete."
    print('Representative coverage:',data['representatives']['coverage'])
