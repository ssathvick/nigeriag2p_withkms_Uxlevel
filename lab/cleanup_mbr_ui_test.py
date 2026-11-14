import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
import test_mbr_db_connection as db
data=json.loads((Path(__file__).parent.parent/'output/mbr-verification/cleanup-ids.json').read_text())
with db.connect() as c:
    with c.cursor() as cur:
        ids=data['submissions']
        cur.execute('SELECT master_id FROM g2p_mbr_submissions WHERE id::text=ANY(%s)',(ids,))
        masters=[row[0] for row in cur.fetchall() if row[0]]
        if data.get('master'):masters.append(data['master'])
        for mid in set(masters):
            # A test master must still carry the exact synthetic test address before cleanup.
            cur.execute('SELECT address_line_1 FROM g2p_register_households WHERE internal_record_id=%s',(mid,))
            row=cur.fetchone()
            if row and row[0]!='E2E synthetic address':raise RuntimeError('Unexpected master data; refusing cleanup')
            cur.execute('DELETE FROM g2p_mbr_master_data WHERE native_id=%s',(mid,))
            cur.execute('DELETE FROM g2p_register_individuals WHERE link_internal_record_id=%s',(mid,))
            cur.execute('DELETE FROM g2p_register_households WHERE internal_record_id=%s',(mid,))
        cur.execute('DELETE FROM g2p_mbr_events WHERE submission_id::text=ANY(%s)',(ids,))
        cur.execute('DELETE FROM g2p_mbr_submissions WHERE id::text=ANY(%s)',(ids,))
print('Removed only the generated MBR UI test records.')
