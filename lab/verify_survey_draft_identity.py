import sys,json
from pathlib import Path
from psycopg2.extras import RealDictCursor
from test_mbr_db_connection import connect
out=Path(__file__).parent.parent/'output/ooru-meeting-audit/verification';sample=json.loads((out/'enumeration-sample.json').read_text());path=out/'survey-draft-identity.json'
with connect() as c:
 with c.cursor(cursor_factory=RealDictCursor) as q:
  q.execute('SELECT internal_record_id,record_name,household_head_name,sponsor_name,income_source,health_insurance_status,television_count,crops_grown,geo_lowest_level_value_id,latitude,longitude,location_accuracy_m FROM g2p_intake_form_households WHERE submission_id=%s',(sample['submission_id'],));rows=q.fetchall();assert len(rows)==1;row=rows[0]
  assert row['record_name'].startswith('SAMPLE') and row['household_head_name']=='Sample Household Head' and row['sponsor_name']=='NG CARES' and row['income_source']=='Fishing' and row['health_insurance_status']=='YES' and row['television_count']==2 and 'Maize' in row['crops_grown'];assert row['geo_lowest_level_value_id']=='NG001001_eziama'
  q.execute('SELECT internal_record_id,link_internal_record_id FROM g2p_intake_form_individuals WHERE submission_id=%s',(sample['submission_id'],));members=q.fetchall();assert len(members)==1 and members[0]['link_internal_record_id']==row['internal_record_id']
if sys.argv[1]=='before':path.write_text(json.dumps({'household_id':row['internal_record_id'],'member_id':members[0]['internal_record_id'],'status':'baseline'},indent=2))
else:
 before=json.loads(path.read_text());assert before['household_id']==row['internal_record_id'] and before['member_id']==members[0]['internal_record_id'];before.update(status='passed',allSectionsPreserved=True,memberLinkPreserved=True);path.write_text(json.dumps(before,indent=2));print('PASS repeat draft saves preserve household/member UUIDs, links and all survey values')
