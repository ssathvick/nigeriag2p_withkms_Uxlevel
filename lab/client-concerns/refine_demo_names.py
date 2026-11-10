import sys,re,json
from pathlib import Path
sys.path.insert(0,'/opt/openg2p-lab/registration');import registration_app as r
root=Path(__file__).parent;backup=Path((root/'backup-location.txt').read_text());changed=[]
with r.pg('register') as c:
 with c.cursor() as q:
  q.execute("SELECT internal_record_id,record_name,household_head_name FROM g2p_register_households WHERE created_by='iqs-synthetic-batch'");rows=q.fetchall();p=backup/'synthetic-household-names.json'
  if not p.exists():p.write_text(json.dumps(rows,default=str))
  for ident,old,head in rows:
   if not head:continue
   head=re.sub(r'\s+Demo(?:\s+\d+)?\b','',head,flags=re.I).strip();name=head+' Household (demonstration)'
   q.execute('UPDATE g2p_register_households SET record_name=%s,household_head_name=%s WHERE internal_record_id=%s AND created_by=%s',(name,head,ident,'iqs-synthetic-batch'));changed.append(ident)
 c.commit()
print('Updated clearly identified synthetic demo household names:',len(changed))
