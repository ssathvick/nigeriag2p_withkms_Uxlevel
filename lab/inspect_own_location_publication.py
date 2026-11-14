import json
from pathlib import Path
from test_mbr_db_connection import connect
s=json.loads((Path(__file__).parent.parent/'output/ooru-meeting-audit/verification/household-parity-location-test.json').read_text())
with connect() as c:
 with c.cursor() as q:q.execute('SELECT latitude,longitude,location_accuracy_m,location_captured_at,geo_lowest_level_value_id FROM g2p_register_households WHERE internal_record_id=%s',(s['internal_id'],));print(q.fetchone())
