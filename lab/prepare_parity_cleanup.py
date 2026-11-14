from pathlib import Path
p=Path(__file__).parent;source=(p/'cleanup_native_meeting_fixtures.py').read_text();body=source[source.index('evidence={};counts={}'):source.index("ledger=Path(")];body=body.replace('fictional-fixture-evidence.json','household-parity-fixture-evidence.json')
header='''import json,datetime
from pathlib import Path
from psycopg2 import sql
from psycopg2.extras import RealDictCursor
from test_mbr_db_connection import connect
ROOT=Path(__file__).parent;out=ROOT.parent/'output/ooru-meeting-audit/verification'
state=json.loads((out/'household-parity-test.json').read_text());assert state['status']=='passed'
ids=[state['id']];intakes=ids[:];roots=[state['internal_id']]
'''
footer='''
(out/'household-parity-fixture-cleanup.json').write_text(json.dumps({'status':'completed','fixture_id':state['id'],'original_records_selected':False,'removed_counts':counts},indent=2));print('Removed only the UUID-tracked full-survey approval test fixture; user-visible sample draft retained.')
'''
(p/'cleanup_household_parity_fixture.py').write_text(header+body+footer)
