from pathlib import Path
from test_mbr_db_connection import connect
root=Path(__file__).parent/'record-security'
with connect() as c:
 with c.cursor() as q:q.execute((root/'schema.sql').read_text());q.execute((root/'policies.sql').read_text())
 c.commit()
print('Transactional record policies refreshed')
